module Placely
  module Settings
    PREF_KEY = 'placely'

    def self.xdi_url
      Sketchup.read_default(PREF_KEY, 'xdi_url', 'https://xdi-production.up.railway.app')
    end

    def self.xdi_url=(url)
      Sketchup.write_default(PREF_KEY, 'xdi_url', url.to_s.strip.chomp('/'))
    end

    def self.open_dialog
      current = xdi_url
      result  = UI.inputbox(
        ['XDi API URL'],
        [current],
        'Placely – Innstillinger'
      )
      return unless result
      new_url = result[0].to_s.strip
      return if new_url.empty?
      self.xdi_url = new_url
      UI.messagebox("XDi URL lagret:\n#{new_url}")
    end
  end
end
