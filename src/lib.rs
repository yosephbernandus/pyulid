use std::{u128, usize};

use pyo3::prelude::*;

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

// #[pyfunction]
// fn ulid() -> PyResult<String> {
//     let mut rng = rand::rng();
//     let random_number: u64 = rng.random();
//     Ok(format!("ULID-{:016X}", random_number))
// }
//
/// A Python module implemented in Rust.
#[pymodule]
fn pyulid(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode_base32, m)?)?;
    m.add_function(wrap_pyfunction!(decode_base32, m)?)?;
    Ok(())
}
