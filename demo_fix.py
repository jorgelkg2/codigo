#!/usr/bin/env python3
"""
Python simulation of the Dart FrequencyMapper to demonstrate the fix
This shows how the frequency mapping issue was resolved
"""

def map_frequency_before_fix(input_str):
    """Simulates the buggy behavior before the fix"""
    if not input_str:
        return ''
    
    # The old code only had mapping for "Martes-Jueves-Sábado"
    # but was missing "Lunes-Miércoles-Viernes"
    
    # First try exact matches (incomplete - missing key mapping)
    exact_matches = {
        'Martes-Jueves-Sábado': 'martes_jueves_sabado',
        'Diario': 'diario',
        'Semanal': 'semanal', 
        'Mensual': 'mensual',
        # BUG: Missing 'Lunes-Miércoles-Viernes' mapping!
    }
    
    if input_str in exact_matches:
        return exact_matches[input_str]
    
    # Try lowercase matches (also incomplete)
    lower_input = input_str.lower()
    lowercase_matches = {
        'martes-jueves-sábado': 'martes_jueves_sabado',
        'diario': 'diario',
        'semanal': 'semanal',
        'mensual': 'mensual',
        # BUG: Missing lowercase version too!
    }
    
    if lower_input in lowercase_matches:
        return lowercase_matches[lower_input]
    
    # PROBLEMATIC: Falls back to emergency case with tildes
    result = input_str.lower().replace(' ', '_').replace('-', '_')
    return result  # This keeps tildes! "lunes_miércoles_viernes"

def map_frequency_after_fix(input_str):
    """Simulates the fixed behavior"""
    if not input_str:
        return ''
    
    # Fixed: Complete mapping with all required frequencies
    exact_matches = {
        'Lunes-Miércoles-Viernes': 'lunes_miercoles_viernes',  # ADDED!
        'Martes-Jueves-Sábado': 'martes_jueves_sabado',
        'Diario': 'diario',
        'Semanal': 'semanal',
        'Mensual': 'mensual',
    }
    
    if input_str in exact_matches:
        return exact_matches[input_str]
    
    # Fixed: Complete lowercase mapping
    lower_input = input_str.lower()
    lowercase_matches = {
        'lunes-miércoles-viernes': 'lunes_miercoles_viernes',  # ADDED!
        'martes-jueves-sábado': 'martes_jueves_sabado',
        'diario': 'diario',
        'semanal': 'semanal',
        'mensual': 'mensual',
    }
    
    if lower_input in lowercase_matches:
        return lowercase_matches[lower_input]
    
    # Fixed: Emergency case now removes tildes for PHP compatibility
    result = (input_str.lower()
              .replace(' ', '_')
              .replace('-', '_')
              .replace('á', 'a')
              .replace('é', 'e')
              .replace('í', 'i')
              .replace('ó', 'o')
              .replace('ú', 'u')
              .replace('ñ', 'n'))
    return result

def main():
    print("Frequency Mapping Fix Demonstration")
    print("=" * 50)
    
    test_cases = [
        'Lunes-Miércoles-Viernes',
        'Martes-Jueves-Sábado', 
        'Diario',
        'lunes-miércoles-viernes',
        'Unknown-Frequency-Ñoño'
    ]
    
    print("\nBEFORE FIX (Buggy Behavior):")
    print("-" * 30)
    for test_case in test_cases:
        result = map_frequency_before_fix(test_case)
        print(f"'{test_case}' → '{result}'")
        if test_case == 'Lunes-Miércoles-Viernes':
            print("  ❌ PROBLEM: Falls to emergency case with tildes!")
    
    print("\nAFTER FIX (Correct Behavior):")
    print("-" * 30)
    for test_case in test_cases:
        result = map_frequency_after_fix(test_case)
        print(f"'{test_case}' → '{result}'")
        if test_case == 'Lunes-Miércoles-Viernes':
            print("  ✅ FIXED: Properly mapped without tildes!")
    
    print("\nKey Changes Made:")
    print("1. Added explicit mapping for 'Lunes-Miércoles-Viernes'")
    print("2. Added lowercase version mapping")
    print("3. Enhanced emergency case to remove Spanish accents")
    print("4. Ensures PHP server compatibility by removing tildes")

if __name__ == "__main__":
    main()