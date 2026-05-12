module Placely
  class WallDialog
    DIALOG_W = 500
    DIALOG_H = 600

    def initialize(group)
      @group = group
    end

    def self.open(group)
      return unless group.is_a?(Sketchup::Group)
      dict = group.attribute_dictionary(SLIMBIM_DICT)
      return UI.messagebox('Ugyldig vegg') unless dict && dict['type'] == 'wall'
      new(group).show
    end

    def self.edit_selected
      sel = Sketchup.active_model.selection.first
      return UI.messagebox('Velg en Placely-vegg først.') unless sel.is_a?(Sketchup::Group)
      dict = sel.attribute_dictionary(SLIMBIM_DICT)
      return UI.messagebox('Valgt objekt er ikke en Placely-vegg.') unless dict && dict['type'] == 'wall'
      new(sel).show
    end

    def show
      dict = @group.attribute_dictionary(SLIMBIM_DICT)

      dialog = UI::HtmlDialog.new(
        dialog_title:    'Placely – Veggegenskaper',
        preferences_key: 'placely_wall_props',
        width:           DIALOG_W,
        height:          DIALOG_H,
        resizable:       true
      )

      html_path = File.join(File.dirname(__FILE__), 'html', 'wall_dialog.html')
      dialog.set_file(html_path)

      dialog.add_action_callback('ready') do |_ctx|
        data = current_data(dict)
        dialog.execute_script("loadData(#{data.to_json})")
      end

      dialog.add_action_callback('save') do |_ctx, json|
        data = JSON.parse(json)
        apply_data(data)
        dialog.close
      end

      dialog.add_action_callback('cancel') { |_ctx| dialog.close }

      dialog.show
    end

    private

    def current_data(dict)
      top_points = WallBuilder.parse_top_points(dict['top_points'])
      length_m   = calc_length(dict)
      {
        'id'             => dict['id'],
        'length_m'       => length_m.round(3),
        'wall_type'      => dict['wall_type'] || DEFAULT_WALL_TYPE,
        'thickness_mm'   => (dict['thickness_m'].to_f * 1000).round,
        'is_roof_driver' => dict['is_roof_driver'] == 'true',
        'top_points'     => top_points
      }
    end

    def apply_data(data)
      model = Sketchup.active_model
      model.start_operation('Placely: Oppdater vegg', true)

      dict = @group.attribute_dictionary(SLIMBIM_DICT, true)
      dict['wall_type']      = data['wall_type']
      dict['thickness_m']    = data['thickness_mm'].to_f / 1000.0
      dict['is_roof_driver'] = data['is_roof_driver'].to_s
      dict['top_points']     = data['top_points'].to_json

      WallBuilder.rebuild(@group)
      model.commit_operation
    end

    def calc_length(dict)
      dx = dict['end_x'].to_f - dict['start_x'].to_f
      dy = dict['end_y'].to_f - dict['start_y'].to_f
      Math.sqrt(dx * dx + dy * dy)
    end
  end
end
