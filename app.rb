require "sinatra"
require "json"

get '/' do
  erb :home
end

post '/timeline' do
  @name = params[:name]
  if no_wiki_article(@name)
    erb :notfound
  else
    # code to get the SOLR link
    get_json(@name, link)
  # get_json("Maruti", "http://localhost:8983/solr/collection1/select/?indent=on&q=Maruti&fl=name,id,date&wt=json")
    erb :timeline
  end
end

helpers do
  def title
    'Time Glider'
  end

  # grab the json from the SOLR link and load it into a ruby hash
  # then populate the hash with the relevant details
  # and return a JSON object corresponding to the modified hash 
  def get_json(name, link)
    # get a link to the JSON returned by Solr
    json_str = `curl "#{link}"`
    json_hash = JSON.load(json_str)

    events = json_hash["response"]["docs"] # events is an array of hashes

    @result = JSON.parse(IO.read('/template.json')) # load the template_hash

    @result["timeline"]["headline"] = "Timeline for #{name}"
    @result["timeline"]["text"] = "<p>Here's the latest news for #{name}.</p>"

    #clear the "date" key from result
    @result["timeline"]["date"] = []

    events.each do |event|
      headline = event["name"]
      date = parse_date(event["date"])
      new_event = { "startDate" => date, "headline" => headline, "text" => "Some filler text" }
      @result["timeline"]["date"].push(new_event)
    end

    JSON.dump(@result)
  end

  # This extracts the TimelineJS-friendly-date from the SOLR response date
  # Sample input: "First Published: 16:30 IST(12/2/2010)"
  # Output: 2010,2,12
  def parse_date(date)
    date[/\d+\/\d+\/\d+/].split('/').reverse.join(',')
  end

  # returns true if the name searched for has no wikipedia article
  # false otherwise
  def no_wiki_article(name)
    search = name.strip.gsub(/ +/, '+') # remove leading/trailing whitespace and replace all spaces in name with +
    result_string = `curl "http://en.wikipedia.org/w/api.php?action=opensearch&search=#{search}"`
    result_json = JSON.load(result_string)[1]
    result_json.empty?
  end
end