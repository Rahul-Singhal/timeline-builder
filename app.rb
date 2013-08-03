require "sinatra"
require "sinatra/activerecord"
require "json"

get '/' do
  erb :home
end

get '/timeline' do
  @name = params[:name]
  # get_json(@name, link)
  # get_json("Maruti", "http://localhost:8983/solr/collection1/select/?indent=on&q=Maruti&fl=name,id,date&wt=json")
  erb :timeline
end

helpers do
  def title
    'Timeline Builder'
  end

  # grab the json from the SOLR link and load it into a ruby hash
  # then populate the hash with the relevant details
  # and return the modified hash
  def get_json(name, link)
    # get a link to the JSON returned by Solr
    json_str = `curl "#{link}"`
    json_hash = JSON.load(json_str)

    events = json_hash["response"]["docs"] # array of events

    result = JSON.parse(IO.read('/template.json')) # load the template_hash
    result["timeline"]["headline"] = "Timeline for #{name}"
    result["timeline"]["text"] = "<p>Here's the latest news for #{name}.</p>"
  end
end