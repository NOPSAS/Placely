# Placely SketchUp Extension – loader
# NOPS AS / Konsepthus AS
# Version 0.1.0

require 'sketchup.rb'
require 'extensions.rb'

module Placely
  unless file_loaded?(__FILE__)
    ext = SketchupExtension.new(
      'Placely Veggverktøy',
      File.join(File.dirname(__FILE__), 'placely', 'extension.rb')
    )
    ext.description = 'Parametrisk veggverktøy med SlimBIM JSON-eksport'
    ext.version     = '0.1.0'
    ext.copyright   = '2026 NOPS AS / Konsepthus AS'
    ext.creator     = 'NOPS AS'
    Sketchup.register_extension(ext, true)
    file_loaded(__FILE__)
  end
end
