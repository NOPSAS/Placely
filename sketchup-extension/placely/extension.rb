require 'json'
require_relative 'constants'
require_relative 'wall_builder'
require_relative 'wall_tool'
require_relative 'wall_dialog'
require_relative 'slimbim_exporter'

module Placely
  unless file_loaded?(__FILE__)
    # --- Meny ---
    placely_menu = UI.menu('Plugins').add_submenu('Placely')

    placely_menu.add_item('Tegn vegg') do
      Sketchup.active_model.select_tool(WallTool.new)
    end

    placely_menu.add_item('Rediger valgt vegg') do
      WallDialog.edit_selected
    end

    placely_menu.add_separator

    placely_menu.add_item('Eksporter SlimBIM JSON') do
      SlimbimExporter.export
    end

    # --- Verktøylinje ---
    toolbar = UI::Toolbar.new('Placely')

    cmd_draw = UI::Command.new('Tegn vegg') do
      Sketchup.active_model.select_tool(WallTool.new)
    end
    cmd_draw.tooltip         = 'Placely: Tegn parametrisk vegg'
    cmd_draw.status_bar_text = 'Klikk for å tegne en Placely-vegg'
    toolbar.add_item(cmd_draw)

    cmd_edit = UI::Command.new('Rediger vegg') do
      WallDialog.edit_selected
    end
    cmd_edit.tooltip = 'Placely: Rediger valgt vegg'
    toolbar.add_item(cmd_edit)

    cmd_export = UI::Command.new('Eksporter SlimBIM') do
      SlimbimExporter.export
    end
    cmd_export.tooltip = 'Placely: Eksporter modell som SlimBIM JSON'
    toolbar.add_item(cmd_export)

    toolbar.restore

    file_loaded(__FILE__)
  end
end
