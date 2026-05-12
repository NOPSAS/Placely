module Placely
  VERSION = '0.1.0'

  # Unit conversion (SketchUp intern enhet er inches)
  M_TO_SU  = 1000.0 / 25.4  # meter → SketchUp inches
  MM_TO_SU = 1.0 / 25.4     # millimeter → SketchUp inches
  SU_TO_M  = 25.4 / 1000.0  # SketchUp inches → meter

  # Standardverdier for nye vegger
  DEFAULT_THICKNESS_M   = 0.248  # Typisk yttervegg
  DEFAULT_WALL_HEIGHT_M = 2.4    # Typisk takhøyde
  DEFAULT_WALL_TYPE     = 'exterior'

  # Navn på AttributeDictionary for SlimBIM-data
  SLIMBIM_DICT = 'slimbim'

  WALL_TYPES = {
    'exterior'    => 'Yttervegg',
    'interior'    => 'Innervegg',
    'load_bearing'=> 'Bærende vegg',
    'partition'   => 'Skillevegg',
    'foundation'  => 'Grunnmur'
  }.freeze
end
