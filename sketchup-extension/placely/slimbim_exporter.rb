module Placely
  module SlimbimExporter
    def self.export
      model  = Sketchup.active_model
      walls  = collect_walls(model)

      if walls.empty?
        UI.messagebox('Ingen Placely-vegger funnet i modellen.\nTegn vegger med Placely-verktøyet først.')
        return
      end

      slimbim = {
        slimbim_version: '1.0.0',
        created_at:      Time.now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        created_by:      "placely-sketchup-v#{VERSION}",
        property: {
          id:       'prop_001',
          type:     'property',
          address:  model.title.empty? ? 'Ukjent adresse' : model.title,
          source_info: { source: 'placely_sketchup', confidence: 1.0 },
          buildings: [{
            id:             'bygg_001',
            type:           'building',
            version_status: 'as_built',
            floors: [{
              id:          'etg_01',
              type:        'floor',
              level_index: 0,
              floor_type:  'ground',
              walls:       walls
            }]
          }]
        }
      }

      default_name = model.title.empty? ? 'modell' : model.title.gsub(/[^a-zA-Z0-9_\-]/, '_')
      path = UI.savepanel('Lagre SlimBIM JSON', '', "#{default_name}_slimbim.json")
      return unless path

      path += '.json' unless path.end_with?('.json')
      File.open(path, 'w:UTF-8') { |f| f.write(JSON.pretty_generate(slimbim)) }
      UI.messagebox("#{walls.length} vegger eksportert til SlimBIM JSON:\n#{path}")
    end

    def self.collect_walls(model)
      walls = []
      model.active_entities.each do |e|
        next unless e.is_a?(Sketchup::Group)
        dict = e.attribute_dictionary(SLIMBIM_DICT)
        next unless dict && dict['type'] == 'wall'
        walls << wall_to_hash(dict)
      end
      walls
    end

    def self.wall_to_hash(dict)
      top_points = WallBuilder.parse_top_points(dict['top_points'])
      {
        id:             dict['id'],
        type:           'wall',
        start:          [dict['start_x'].to_f.round(4), dict['start_y'].to_f.round(4), dict['start_z'].to_f.round(4)],
        end:            [dict['end_x'].to_f.round(4),   dict['end_y'].to_f.round(4),   dict['end_z'].to_f.round(4)],
        thickness_m:    dict['thickness_m'].to_f.round(4),
        wall_type:      dict['wall_type'] || 'exterior',
        is_roof_driver: dict['is_roof_driver'] == 'true',
        top_points:     top_points.map { |tp| { x_m: tp[0].round(4), z_m: tp[1].round(4) } },
        source_info: {
          source:     dict['source'] || 'placely_sketchup',
          confidence: 1.0
        }
      }
    end
  end
end
