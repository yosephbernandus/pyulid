use std::{u128, usize};

use pyo3::prelude::*;
use rand::Rng;
use std::time::{SystemTime, UNIX_EPOCH};

// Crockford's Base32 alphabet (exclude I, L, O, U)
const ALPHABET: &[u8; 32] = b"0123456789ABCDEFGHJKMNPQRSTVWXYZ";

#[pyfunction]
fn encode_base32(number: u128) -> PyResult<String> {
    if number == 0 {
        return Ok("0".to_string());
    }

    let mut result = String::new();
    let mut n = number;

    while n > 0 {
        let remainder = (n % 32) as usize;
        result.insert(0, ALPHABET[remainder] as char);
        n /= 32;
    }

    Ok(result)
}

#[pyfunction]
fn decode_base32(encoded: &str) -> PyResult<u128> {
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

        result = result * 32 + value;
    }

    Ok(result)
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

fn encode_base32_internal(number: u128) -> String {
    if number == 0 {
        return "0".to_string();
    }

    let mut result = String::new();
    let mut n = number;

    while n > 0 {
        let remainder = (n % 32) as usize;
        result.insert(0, ALPHABET[remainder] as char);
        n /= 32;
    }

    while result.len() < 26 {
        result.insert(0, '0');
    }

    return result;
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

        result = result * 32 + value;
    }

    Ok(result)
}

#[pyfunction]
fn ulid() -> PyResult<String> {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64;

    let mut rng = rand::rng();
    let random: u128 = rng.random::<u128>() & Ulid::bitmask(80);

    let ulid = Ulid::from_parts(timestamp, random);
    Ok(ulid.to_string())
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

    Ok(())
}
