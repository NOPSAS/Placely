# Placely XDi Importer
# Sender plantegninger/PDF til XDi API og oppretter vegger i SketchUp.
require 'net/http'
require 'json'
require 'uri'
require 'tempfile'

module Placely
  module XdiImporter
    TIMEOUT_SEC = 120

    def self.xdi_url
      Settings.xdi_url
    end

    def self.import_from_file
      # 1. Velg fil
      path = UI.openpanel(
        'Velg tegning for XDi-import',
        '',
        'Byggetegning|*.pdf;*.png;*.jpg;*.jpeg||PDF|*.pdf||PNG|*.png||JPG|*.jpg;*.jpeg||'
      )
      return unless path

      # 2. Adresse (valgfritt)
      input = UI.inputbox(
        ['Adresse (valgfritt)', 'Tilleggskontekst (f.eks. fasadetegning sør)'],
        ['', ''],
        'Placely – XDi Import'
      )
      return unless input

      address, context = input

      # 3. Velg endepunkt basert på filtype
      ext      = File.extname(path).downcase
      endpoint = ext == '.pdf' ? '/parse/pdf' : '/parse/image'

      Sketchup.status_text = 'Placely: Sender til XDi – vennligst vent...'

      # 4. Kall XDi
      result = call_xdi(path, endpoint, address, context)
      Sketchup.status_text = ''
      return unless result

      # 5. Bygg vegger
      walls_created = build_from_slimbim(result)
      rooms = count_rooms(result)

      UI.messagebox(
        "XDi-import ferdig!\n\n" \
        "#{walls_created} vegger opprettet\n" \
        "#{rooms} rom funnet\n\n" \
        "Kilde: #{result.dig('created_by') || 'XDi'}"
      )
    end

    def self.check_health
      uri = URI("#{xdi_url}/health")
      resp = Net::HTTP.get_response(uri)
      resp.code == '200'
    rescue
      false
    end

    private

    def self.call_xdi(file_path, endpoint, address, context)
      unless check_health
        UI.messagebox(
          "Klarte ikke å nå XDi API på #{xdi_url}\n\n" \
          "Start XDi:\n  cd xdi\n  python main.py"
        )
        return nil
      end

      uri      = URI("#{xdi_url}#{endpoint}")
      boundary = "PlacelyBoundary#{Time.now.to_i}"

      body = build_multipart(file_path, address, context, boundary)

      req = Net::HTTP::Post.new(uri)
      req['Content-Type'] = "multipart/form-data; boundary=#{boundary}"
      req.body = body

      resp = Net::HTTP.start(uri.hostname, uri.port, read_timeout: TIMEOUT_SEC) { |h| h.request(req) }

      if resp.code == '200'
        JSON.parse(resp.body)
      else
        UI.messagebox("XDi feil (#{resp.code}):\n#{resp.body[0, 300]}")
        nil
      end
    rescue => e
      UI.messagebox("XDi-kall feilet:\n#{e.message}")
      nil
    end

    def self.build_multipart(file_path, address, context, boundary)
      file_data = File.binread(file_path)
      file_name = File.basename(file_path)
      ext       = File.extname(file_path).downcase
      mime      = case ext
                  when '.pdf'        then 'application/pdf'
                  when '.png'        then 'image/png'
                  when '.jpg', '.jpeg' then 'image/jpeg'
                  else 'application/octet-stream'
                  end

      body = ''.b  # binary string
      body << "--#{boundary}\r\n".b
      body << "Content-Disposition: form-data; name=\"file\"; filename=\"#{file_name}\"\r\n".b
      body << "Content-Type: #{mime}\r\n\r\n".b
      body << file_data
      body << "\r\n".b

      body << "--#{boundary}\r\n".b
      body << "Content-Disposition: form-data; name=\"address\"\r\n\r\n".b
      body << address.to_s.b
      body << "\r\n".b

      unless context.to_s.empty?
        body << "--#{boundary}\r\n".b
        body << "Content-Disposition: form-data; name=\"context\"\r\n\r\n".b
        body << context.to_s.b
        body << "\r\n".b
      end

      body << "--#{boundary}--\r\n".b
      body
    end

    def self.build_from_slimbim(doc)
      walls_data = []
      (doc.dig('property', 'buildings') || []).each do |building|
        (building['floors'] || []).each do |floor|
          (floor['walls'] || []).each { |w| walls_data << w }
        end
      end

      return 0 if walls_data.empty?

      model = Sketchup.active_model
      model.start_operation('Placely: XDi Import', true)

      count = 0
      walls_data.each do |wd|
        group = build_single_wall(wd)
        count += 1 if group
      end

      model.commit_operation
      count
    end

    def self.build_single_wall(wd)
      sa = wd['start'] || [0, 0, 0]
      ea = wd['end']   || [1, 0, 0]

      start_pt = Geom::Point3d.new(sa[0].to_f * M_TO_SU, sa[1].to_f * M_TO_SU, sa[2].to_f * M_TO_SU)
      end_pt   = Geom::Point3d.new(ea[0].to_f * M_TO_SU, ea[1].to_f * M_TO_SU, ea[2].to_f * M_TO_SU)

      return nil if start_pt.distance(end_pt) < MM_TO_SU * 50

      raw_tp   = wd['top_points'] || []
      top_pts  = raw_tp.map { |tp| [tp['x_m'].to_f, tp['z_m'].to_f] }
      if top_pts.empty?
        len = start_pt.distance(end_pt) * SU_TO_M
        top_pts = [[0.0, DEFAULT_WALL_HEIGHT_M], [len.round(3), DEFAULT_WALL_HEIGHT_M]]
      end

      props = {
        id:         wd['id'] || "wall_#{Time.now.to_i}_#{rand(9999)}",
        start:      start_pt,
        end_pt:     end_pt,
        thickness:  (wd['thickness_m'] || DEFAULT_THICKNESS_M).to_f,
        wall_type:  wd['wall_type'] || DEFAULT_WALL_TYPE,
        top_points: top_pts,
        source:     'xdi_import'
      }

      WallBuilder.build(props)
    end

    def self.count_rooms(doc)
      count = 0
      (doc.dig('property', 'buildings') || []).each do |b|
        (b['floors'] || []).each { |f| count += (f['rooms'] || []).length }
      end
      count
    end
  end
end
