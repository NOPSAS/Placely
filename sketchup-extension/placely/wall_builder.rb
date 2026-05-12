module Placely
  module WallBuilder
    def self.build(props)
      model = Sketchup.active_model
      model.start_operation('Placely: Legg til vegg', true)

      begin
        group = model.active_entities.add_group
        group.name = "PH_Wall_#{props[:id]}"
        store_slimbim_data(group, props)
        rebuild_geometry(group, props)
        model.commit_operation
        group
      rescue => e
        model.abort_operation
        UI.messagebox("Placely feil ved bygging:\n#{e.message}")
        nil
      end
    end

    # Bygg geometri på nytt fra SlimBIM-data lagret på gruppen
    def self.rebuild(group)
      dict = group.attribute_dictionary(SLIMBIM_DICT)
      return unless dict

      props = {
        start:      su_pt(dict['start_x'], dict['start_y'], dict['start_z']),
        end_pt:     su_pt(dict['end_x'],   dict['end_y'],   dict['end_z']),
        thickness:  dict['thickness_m'].to_f,
        top_points: parse_top_points(dict['top_points'])
      }

      model = Sketchup.active_model
      model.start_operation('Placely: Oppdater vegg', true)
      rebuild_geometry(group, props)
      model.commit_operation
    end

    def self.rebuild_geometry(group, props)
      group.entities.clear!

      start_pt     = props[:start]
      end_pt       = props[:end_pt]
      thickness_su = props[:thickness].to_f * M_TO_SU
      top_points   = props[:top_points]

      return if top_points.length < 2

      wall_dir = (end_pt - start_pt).normalize
      # Perpendikulær i horisontalplanet (venstre for veggretning)
      perp = Geom::Vector3d.new(-wall_dir.y, wall_dir.x, 0)
      base_z = start_pt.z
      entities = group.entities

      # Bygg én face per segment mellom to knekkpunkter
      top_points.each_with_index do |tp, i|
        ntp = top_points[i + 1]
        break unless ntp

        x1 = tp[0].to_f  * M_TO_SU
        z1 = tp[1].to_f  * M_TO_SU
        x2 = ntp[0].to_f * M_TO_SU
        z2 = ntp[1].to_f * M_TO_SU

        next if (x2 - x1).abs < MM_TO_SU  # ignorer degenererte segmenter

        bl = Geom::Point3d.new(start_pt.x + wall_dir.x * x1, start_pt.y + wall_dir.y * x1, base_z)
        br = Geom::Point3d.new(start_pt.x + wall_dir.x * x2, start_pt.y + wall_dir.y * x2, base_z)
        tr = Geom::Point3d.new(start_pt.x + wall_dir.x * x2, start_pt.y + wall_dir.y * x2, base_z + z2)
        tl = Geom::Point3d.new(start_pt.x + wall_dir.x * x1, start_pt.y + wall_dir.y * x1, base_z + z1)

        begin
          face = entities.add_face([bl, br, tr, tl])
          next unless face.is_a?(Sketchup::Face)
          # Sørg for at flatenormalen peker utover (i perp-retningen)
          face.reverse! unless face.normal.dot(perp) > 0
          # Pushpull innover (negativt = mot normalen) for å lage solid
          face.pushpull(-thickness_su)
        rescue => e
          puts "Placely WallBuilder segment #{i}: #{e.message}"
        end
      end
    end

    def self.store_slimbim_data(group, props)
      dict = group.attribute_dictionary(SLIMBIM_DICT, true)
      s = props[:start]
      e = props[:end_pt]

      dict['id']             = props[:id]
      dict['type']           = 'wall'
      dict['wall_type']      = props[:wall_type] || DEFAULT_WALL_TYPE
      dict['thickness_m']    = props[:thickness].to_f
      dict['is_roof_driver'] = 'false'
      dict['source']         = props[:source] || "placely-sketchup-v#{VERSION}"

      dict['start_x'] = (s.x * SU_TO_M).round(6)
      dict['start_y'] = (s.y * SU_TO_M).round(6)
      dict['start_z'] = (s.z * SU_TO_M).round(6)
      dict['end_x']   = (e.x * SU_TO_M).round(6)
      dict['end_y']   = (e.y * SU_TO_M).round(6)
      dict['end_z']   = (e.z * SU_TO_M).round(6)

      dict['top_points'] = props[:top_points].to_json
    end

    def self.parse_top_points(raw)
      JSON.parse(raw.to_s)
    rescue
      [[0.0, DEFAULT_WALL_HEIGHT_M], [1.0, DEFAULT_WALL_HEIGHT_M]]
    end

    def self.su_pt(x_m, y_m, z_m)
      Geom::Point3d.new(x_m.to_f * M_TO_SU, y_m.to_f * M_TO_SU, z_m.to_f * M_TO_SU)
    end
  end
end
