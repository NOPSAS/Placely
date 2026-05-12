module Placely
  class WallTool
    def initialize
      @phase     = :idle   # :idle | :placing
      @start_pt  = nil
      @end_pt    = nil
      @lock_axis = nil     # nil | :red | :green
      @ip        = Sketchup::InputPoint.new
    end

    # --- SketchUp Tool-protokoll ---

    def activate
      update_statusbar
      Sketchup.active_model.active_view.invalidate
    end

    def deactivate(view)
      view.invalidate
    end

    def resume(view)
      update_statusbar
      view.invalidate
    end

    def onMouseMove(_flags, x, y, view)
      @ip.pick(view, x, y)
      raw = @ip.position
      @end_pt = (@lock_axis && @start_pt) ? constrain(raw, @start_pt, @lock_axis) : raw
      view.tooltip = @ip.tooltip
      view.invalidate
    end

    def onLButtonDown(_flags, x, y, view)
      @ip.pick(view, x, y)

      case @phase
      when :idle
        @start_pt = @ip.position.clone
        @phase    = :placing
        update_statusbar
      when :placing
        finish_wall
        @start_pt = @end_pt.clone  # kjed neste vegg
      end

      view.invalidate
    end

    def onLButtonDoubleClick(_flags, _x, _y, _view)
      Sketchup.active_model.select_tool(nil)
    end

    def onKeyDown(key, _repeat, _flags, view)
      case key
      when 27  # ESC
        if @phase == :placing
          @phase    = :idle
          @start_pt = nil
        else
          Sketchup.active_model.select_tool(nil)
        end
      when 37  # Venstrepil → lås grønn akse
        @lock_axis = (@lock_axis == :green) ? nil : :green
      when 39  # Høyrepil  → lås rød akse
        @lock_axis = (@lock_axis == :red) ? nil : :red
      when 16  # Shift → frigjør lås
        @lock_axis = nil
      end

      update_statusbar
      view.invalidate
      false
    end

    def draw(view)
      return unless @phase == :placing && @start_pt && @end_pt

      color = case @lock_axis
              when :red   then Sketchup::Color.new('red')
              when :green then Sketchup::Color.new('green')
              else             Sketchup::Color.new(30, 120, 255)
              end

      view.drawing_color = color
      view.line_width    = 2
      view.draw(GL_LINES, [@start_pt, @end_pt])

      dist_m = (@start_pt.distance(@end_pt) * SU_TO_M).round(3)
      mid    = Geom::Point3d.linear_combination(0.5, @start_pt, 0.5, @end_pt)
      view.draw_text(mid, "#{dist_m} m")
    end

    def getMenu(menu)
      menu.add_item('Avslutt veggverktøy') { Sketchup.active_model.select_tool(nil) }
    end

    private

    def constrain(pt, origin, axis)
      case axis
      when :red   then Geom::Point3d.new(pt.x, origin.y, origin.z)
      when :green then Geom::Point3d.new(origin.x, pt.y, origin.z)
      end
    end

    def finish_wall
      return unless @start_pt && @end_pt
      return if @start_pt.distance(@end_pt) < MM_TO_SU * 50  # ignorer < 50 mm

      length_m = @start_pt.distance(@end_pt) * SU_TO_M
      wall_id  = "wall_#{Time.now.to_i}_#{rand(9999)}"

      props = {
        id:         wall_id,
        start:      @start_pt.clone,
        end_pt:     @end_pt.clone,
        thickness:  DEFAULT_THICKNESS_M,
        wall_type:  DEFAULT_WALL_TYPE,
        top_points: [[0.0, DEFAULT_WALL_HEIGHT_M], [length_m.round(3), DEFAULT_WALL_HEIGHT_M]],
        source:     "placely-sketchup-v#{VERSION}"
      }

      group = WallBuilder.build(props)
      WallDialog.open(group) if group
    end

    def update_statusbar
      if @phase == :idle
        Sketchup.status_text = 'Placely | Klikk for å starte vegg  ·  ESC: Avslutt'
      else
        lock_txt = case @lock_axis
                   when :red   then '  ·  Låst: RØD'
                   when :green then '  ·  Låst: GRØNN'
                   else ''
                   end
        Sketchup.status_text = "Placely | Klikk for å avslutte  ·  ← Grønn  → Rød  ·  Shift: Frigjør  ·  ESC: Avbryt#{lock_txt}"
      end
    end
  end
end
