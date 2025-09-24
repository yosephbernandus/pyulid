use std::{
    sync::{Mutex, OnceLock},
    usize,
};

use pyo3::prelude::*;
use rand::Rng;
use std::time::{SystemTime, UNIX_EPOCH};

// Unified ULID state for both regular and monotonic generation
static ULID_STATE: OnceLock<Mutex<UlidState>> = OnceLock::new();

// Crockford's Base32 alphabet (exclude I, L, O, U)
const ALPHABET: &[u8; 32] = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ";

#[derive(Debug)]
struct UlidState {
    last_timestamp: u64,
    last_random: u128,
    timestamp_str: [u8; 10], // Pre-encoded timestamp
    buffer: [u8; 26],        // Reusable buffer for string construction
}

impl UlidState {
    fn new() -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;

        let mut rng = rand::rng();
        let random = rng.random::<u128>() & Ulid::bitmask(80);

        // Pre-encode initial timestamp
        let timestamp_str = encode_timestamp(timestamp);

        UlidState {
            last_timestamp: timestamp,
            last_random: random,
            timestamp_str,
            buffer: [b'0'; 26],
        }
    }

    /// string generation using pre-cached timestamp encoding
    #[inline(always)]
    fn generate_string(&mut self, monotonic: bool) -> Result<String, String> {
        let current_timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;

        // Update state
        if current_timestamp == self.last_timestamp {
            if self.last_random == Ulid::bitmask(80) {
                if monotonic {
                    return Err(
                        "Random component overflow, too many ULIDs in same millisecond".to_string(),
                    );
                } else {
                    let mut rng = rand::rng();
                    self.last_random = rng.random::<u128>() & Ulid::bitmask(80);
                }
            } else {
                self.last_random += 1;
            }
        } else if current_timestamp > self.last_timestamp {
            self.last_timestamp = current_timestamp;
            let mut rng = rand::rng();
            self.last_random = rng.random::<u128>() & Ulid::bitmask(80);
            self.timestamp_str = encode_timestamp(current_timestamp);
        } else {
            if monotonic {
                return Err("Clock moved backwards, cannot generate monotonic ULID".to_string());
            } else {
                if self.last_random == Ulid::bitmask(80) {
                    let mut rng = rand::rng();
                    self.last_random = rng.random::<u128>() & Ulid::bitmask(80);
                } else {
                    self.last_random += 1;
                }
            }
        }

        // String construction using cached timestamp
        let random_bytes = encode_random(self.last_random);
        self.buffer[0..10].copy_from_slice(&self.timestamp_str);
        self.buffer[10..26].copy_from_slice(&random_bytes);

        Ok(unsafe { String::from_utf8_unchecked(self.buffer.to_vec()) })
    }
}

#[pyfunction]
fn encode_base32(number: u128) -> PyResult<String> {
    Ok(encode_base32_internal(number))
}

#[pyfunction]
fn decode_base32(encoded: &str) -> PyResult<u128> {
    decode_base32_internal(encoded)
}

#[derive(Debug, Clone, Copy)]
pub struct Ulid(u128);

impl Ulid {
    const TIME_BITS: u8 = 48;
    const RAND_BITS: u8 = 80;

    pub fn from_parts(timestamp_ms: u64, random: u128) -> Self {
        let time_part = (timestamp_ms as u128) & Self::bitmask(Self::TIME_BITS);
        let rand_part = random & Self::bitmask(Self::RAND_BITS);
        Ulid((time_part << Self::RAND_BITS) | rand_part)
    }

    pub fn timestamp_ms(&self) -> u64 {
        (self.0 >> Self::RAND_BITS) as u64
    }

    pub fn random(&self) -> u128 {
        self.0 & Self::bitmask(Self::RAND_BITS)
    }

    pub fn to_string(&self) -> String {
        encode_base32_internal(self.0)
    }

    const fn bitmask(len: u8) -> u128 {
        (1 << len) - 1
    }
}

fn encode_base32_internal(mut number: u128) -> String {
    let mut buffer = [b'0'; 26]; // Pre-allocated array
    let mut pos = 25;
    while number > 0 && pos > 0 {
        buffer[pos] = ALPHABET[(number & 0x1f) as usize]; // Direct access to mem pre-allocated
        number >>= 5;
        pos -= 1;
    }

    String::from_utf8(buffer.to_vec()).unwrap()
}

fn decode_base32_internal(encoded: &str) -> Result<u128, pyo3::PyErr> {
    let mut result: u128 = 0;

    for c in encoded.chars() {
        let value = match ALPHABET
            .iter()
            .position(|&x| x as char == c.to_ascii_uppercase())
        {
            Some(pos) => pos as u128,
            None => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Invalid character '{}' in Base32 string",
                    c
                )))
            }
        };

        result = (result << 5) | value; // Bit shift
    }

    Ok(result)
}

#[inline(always)]
fn encode_timestamp(mut timestamp: u64) -> [u8; 10] {
    let mut buffer = [b'0'; 10];

    // Encode from right to left
    for i in (0..10).rev() {
        buffer[i] = ALPHABET[(timestamp & 0x1F) as usize];
        timestamp >>= 5; // Bit shift equals to n /= 32
    }

    buffer
}

#[inline(always)]
fn encode_random(mut random: u128) -> [u8; 16] {
    let mut buffer = [b'0'; 16];

    // Encode from right to left like
    for i in (0..16).rev() {
        buffer[i] = ALPHABET[(random & 0x1F) as usize];
        random >>= 5; // Bit shift instead of division
    }

    buffer
}

#[pyfunction]
fn ulid() -> PyResult<String> {
    let state_mutex = ULID_STATE.get_or_init(|| Mutex::new(UlidState::new()));
    let mut state = state_mutex.lock().unwrap();

    match state.generate_string(false) {
        Ok(ulid_str) => Ok(ulid_str),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
    }
}

#[pyfunction]
fn ulid_timestamp(ulid_str: &str) -> PyResult<u64> {
    if ulid_str.len() != 26 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "ULID must be exactly 26 characters",
        ));
    }

    let decoded = decode_base32_internal(ulid_str)?;
    let ulid = Ulid(decoded);

    Ok(ulid.timestamp_ms())
}

#[pyfunction]
fn ulid_random(ulid_str: &str) -> PyResult<u128> {
    if ulid_str.len() != 26 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "ULID must be exactly 26 characters",
        ));
    }

    let decoded = decode_base32_internal(ulid_str)?;
    let ulid = Ulid(decoded);

    Ok(ulid.random())
}

#[pyfunction]
fn ulid_is_valid(ulid_str: &str) -> bool {
    if ulid_str.len() != 26 {
        return false;
    }

    // Validation to check all characters is base 32
    ulid_str
        .chars()
        .all(|c| ALPHABET.contains(&(c.to_ascii_uppercase() as u8)))
}

#[pyfunction]
fn ulid_with_timestamp(timestamp_ms: u64) -> PyResult<String> {
    let mut rng = rand::rng();
    let random: u128 = rng.random::<u128>() & Ulid::bitmask(80);
    let ulid = Ulid::from_parts(timestamp_ms, random);
    Ok(ulid.to_string())
}

#[pyfunction]
fn ulid_to_uuid(ulid_str: &str) -> PyResult<String> {
    if ulid_str.len() != 26 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "ULID must be exactly 26 characters",
        ));
    }

    let decoded = decode_base32_internal(ulid_str)?;

    let hex = format!("{:032x}", decoded);
    let uuid = format!(
        "{}-{}-{}-{}-{}",
        &hex[0..8],
        &hex[8..12],
        &hex[12..16],
        &hex[16..20],
        &hex[20..32]
    );

    Ok(uuid)
}

#[pyfunction]
fn uuid_to_ulid(uuid_str: &str) -> PyResult<String> {
    let hex_only: String = uuid_str.chars().filter(|c| *c != '-').collect();

    if hex_only.len() != 32 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "UUID must be 32 hex characters (with or without dashes)",
        ));
    }

    let decoded = u128::from_str_radix(&hex_only, 16)
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid hex characters in UUID"))?;

    Ok(encode_base32_internal(decoded))
}

#[pyfunction]
fn ulid_monotonic() -> PyResult<String> {
    let state_mutex = ULID_STATE.get_or_init(|| Mutex::new(UlidState::new()));
    let mut state = state_mutex.lock().unwrap();

    // Use strict monotonic mode (monotonic = true) - errors on overflow/clock issues
    match state.generate_string(true) {
        Ok(ulid_str) => Ok(ulid_str),
        Err(err) => Err(pyo3::exceptions::PyRuntimeError::new_err(err)),
    }
}

#[pyfunction]
fn ulid_from_str(ulid_str: &str) -> PyResult<String> {
    if ulid_str.len() != 26 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "ULID must be exactly 26 characters",
        ));
    }

    if !ulid_is_valid(ulid_str) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Invalid ULID string format",
        ));
    }

    // Return normalized (uppercase) version
    Ok(ulid_str.to_ascii_uppercase())
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyulid(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode_base32, m)?)?;
    m.add_function(wrap_pyfunction!(decode_base32, m)?)?;
    m.add_function(wrap_pyfunction!(ulid, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_timestamp, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_random, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_is_valid, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_with_timestamp, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_to_uuid, m)?)?;
    m.add_function(wrap_pyfunction!(uuid_to_ulid, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_monotonic, m)?)?;
    m.add_function(wrap_pyfunction!(ulid_from_str, m)?)?;
    Ok(())
}
