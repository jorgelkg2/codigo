// Frequency mapping utility for converting dropdown frequency values
// to database-compatible format

class FrequencyMapper {
  /// Maps frequency strings from dropdown format to database format
  /// Handles Spanish frequency patterns with proper accent removal
  static String mapFrequency(String input) {
    if (input.isEmpty) return '';
    
    // First try exact matches for common patterns
    switch (input) {
      case 'Lunes-Miércoles-Viernes':
        return 'lunes_miercoles_viernes'; // Fixed: removed tilde from 'miércoles'
      case 'Martes-Jueves-Sábado':
        return 'martes_jueves_sabado'; // Fixed: removed tilde from 'sábado'
      case 'Diario':
        return 'diario';
      case 'Semanal':
        return 'semanal';
      case 'Mensual':
        return 'mensual';
    }

    // Try lowercase matches
    String lowerInput = input.toLowerCase();
    switch (lowerInput) {
      case 'lunes-miércoles-viernes':
        return 'lunes_miercoles_viernes';
      case 'martes-jueves-sábado':
        return 'martes_jueves_sabado';
      case 'diario':
        return 'diario';
      case 'semanal':
        return 'semanal';
      case 'mensual':
        return 'mensual';
    }

    // Default case: normalize the input by removing accents and converting format
    String result = input.toLowerCase()
        .replaceAll(' ', '_')
        .replaceAll('-', '_')
        // Remove Spanish accents to ensure PHP server compatibility
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ñ', 'n');

    return result;
  }

  /// Gets all supported frequency options for dropdown
  static List<String> getSupportedFrequencies() {
    return [
      'Lunes-Miércoles-Viernes',
      'Martes-Jueves-Sábado',
      'Diario',
      'Semanal',
      'Mensual',
    ];
  }

  /// Validates if a frequency is supported
  static bool isValidFrequency(String frequency) {
    return getSupportedFrequencies().contains(frequency);
  }
}