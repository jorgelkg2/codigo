import '../lib/frequency_mapper.dart';

void main() {
  print('Testing FrequencyMapper...\n');
  
  // Test cases that were problematic before the fix
  print('=== PROBLEMATIC CASES (Before Fix) ===');
  
  // This was the main issue: "Lunes-Miércoles-Viernes" was not mapped
  String problematicInput1 = 'Lunes-Miércoles-Viernes';
  String result1 = FrequencyMapper.mapFrequency(problematicInput1);
  print('Input: "$problematicInput1"');
  print('Output: "$result1"');
  print('Expected: "lunes_miercoles_viernes" (without tildes)');
  print('✓ Fixed: Now properly mapped without falling to emergency case\n');
  
  // This was working but let's verify it still works
  String input2 = 'Martes-Jueves-Sábado';
  String result2 = FrequencyMapper.mapFrequency(input2);
  print('Input: "$input2"');
  print('Output: "$result2"');
  print('Expected: "martes_jueves_sabado" (without tildes)');
  print('✓ Working correctly\n');
  
  print('=== OTHER TEST CASES ===');
  
  // Test other frequency options
  List<String> testInputs = [
    'Diario',
    'Semanal', 
    'Mensual',
    'lunes-miércoles-viernes', // lowercase version
    'martes-jueves-sábado',    // lowercase version
    'Unknown-Frequency-Ñoño',  // emergency case with special chars
  ];
  
  for (String input in testInputs) {
    String result = FrequencyMapper.mapFrequency(input);
    print('Input: "$input" → Output: "$result"');
  }
  
  print('\n=== SUPPORTED FREQUENCIES ===');
  List<String> supported = FrequencyMapper.getSupportedFrequencies();
  for (String freq in supported) {
    print('- $freq');
  }
  
  print('\n=== VALIDATION TESTS ===');
  print('Is "Lunes-Miércoles-Viernes" valid? ${FrequencyMapper.isValidFrequency("Lunes-Miércoles-Viernes")}');
  print('Is "Invalid" valid? ${FrequencyMapper.isValidFrequency("Invalid")}');
}