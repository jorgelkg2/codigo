# Codigo - Frequency Mapping Fix

This repository contains the fix for the frequency mapping bug where "Lunes-Miércoles-Viernes" was not properly converted to a PHP-compatible format.

## Issue Fixed

The application had a bug where Spanish frequency strings with tildes were not properly processed by the PHP backend. See [FREQUENCY_FIX_README.md](FREQUENCY_FIX_README.md) for detailed information.

## Files

- `lib/frequency_mapper.dart` - Fixed frequency mapping utility
- `test/frequency_mapper_test.dart` - Test cases
- `demo_fix.py` - Demonstration of the fix
- `FREQUENCY_FIX_README.md` - Detailed fix documentation