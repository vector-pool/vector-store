import torch
import bittensor as bt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vectornet.embedding.embed import TextToEmbedding
from vectornet.wiki_integraion.wiki_scraper import get_wiki_article_content_with_pageid

def evaluate_create_request(response, validator_db_manager, query, pageids):
    
    if response is None:
        bt.logging.error("aresponse doesn't have a value")
        return 0
    if len(response) != 4:
        bt.logging.error("response's length is not 4, it contains less or more ingegers.")
        return 0
    if not response[3]:
        bt.logging.error("It returns empty validator_id list, it may cause validator sent empty index_data")
    user_id, organization_id, namespace_id, vector_ids = get_ids_from_response(response)
    db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
    if db_user_id:
        if db_user_name != query.user_name:
            return 0
    if db_organization_id:
        if db_organization_name != query.organization_name:
            return 0
    if db_namespace_id is not None:
        return 0
    if len(pageids) != len(vector_ids):
        return 0
    return 1
    
        
def evaluate_update_request(query, response, query_user_id, query_organization_id, query_namespace_id, pageids):
    
    if response is None:
        bt.logging.error("update request response doesn't have a value")
        return 0
    if len(response) != 4:
        bt.logging.error("response's length is not 3, it contains less or more ingegers.")
        return 0
    response_user_id, response_organization_id, response_namespace_id, vector_ids = get_ids_from_response(response)
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        return 0
    if len(pageids) != len(vector_ids):
        return 0
    
    return 1

def evaluate_delete_request(query, response, query_user_id, query_organization_id, query_namespace_id,):
    
    if response is None:
        return 0
    if len(response) != 3:
        return 0
    response_user_id, response_organization_id, response_namespace_id = response
    
    if (
        query_user_id != response_user_id or
        query_organization_id != response_organization_id or
        query_namespace_id != response_namespace_id
    ):
        return 0
    
    return 1
    
def evaluate_read_request(query, response, original_content):
    
    zero_score = 1
    score = 0
    
    ids = response[0]
    content = response[1]
    
    if (
        ids is None or
        content is None
    ):
        zero_score = 0
    if (
        ids[0] != query.user_id or
        ids[1] != query.organization_id or
        ids[2] != query.namespace_id
    ):
        zero_score = 0
    get_wiki_article_content_with_pageid
    contents = get_wiki_contents_with(ids)
    if content not in contents:
        return 0
    if content == original_content:
        score = 1
    else:
        score = evaluate_similarity(original_content, content)
    return score * zero_score
        
def evaluate_similarity(original_content, content):
    
    embedding_manager = TextToEmbedding()
    original_embedding_tensor = embedding_manager.embed(original_content)[1][0]
    content_embedding_tensor = embedding_manager.embed(content)[1][0]
    original_content_embedding_np = original_embedding_tensor.detach().numpy().reshape(1, -1)
    content_embedding_np = content_embedding_tensor.detach().numpy().reshape(1, -1)
        
    similarity_score = cosine_similarity(original_content_embedding_np, content_embedding_np)[0][0]

    return similarity_score
    
def get_ids_from_response(response):
    return response[0], response[1], response[2], response[3]

if __name__ == '__main__':
    original_content = "The following outline is provided as an overview of and topical guide to dance: Dance – human movement either used as a form of expression or presented in a social, spiritual or performance setting. Choreography is the art of making dances, and the person who does this is called a choreographer. Definitions of what constitutes dance are dependent on social, cultural, aesthetic, artistic and moral constraints and range from functional movement (such as Folk dance) to codified, virtuoso techniques such as ballet. A great many dances and dance styles are performed to dance music. == What type of thing is dance? == Dance (also called dancing) can fit the following categories: an activity or behavior one of the arts – a creative endeavor or discipline. one of the performing arts. Hobby – regular activity or interest that is undertaken for pleasure, typically done during ones leisure time. Exercise – bodily activity that enhances or maintains physical fitness and overall health and wellness. Sport—bodily activity that displays physical exertion Recreation – leisure time activity Ritual Some other things can be named dance metaphorically; see dance (disambiguation) == Types of dance == Type of dance – a particular dance or dance style. There are many varieties of dance. Dance categories are not mutually exclusive. For example, tango is traditionally a partner dance. While it is mostly social dance, its ballroom form may be competitive dance, as in DanceSport. At the same time it is enjoyed as performance dance, whereby it may well be a solo dance. List of dances List of dance style categories List of ethnic, regional, and folk dances by origin List of folk dances sorted by origin List of national dances List of DanceSport dances === Dance genres === === Dance styles by number of interacting dancers === Solo dance – a dance danced by an individual dancing alone. Partner dance – dance with just 2 dancers, dancing together. In most partner dances, one, typically a man, is the leader; the other, typically a woman, is the follower. As a rule, they maintain connection with each other. In some dances the connection is loose and called dance handhold. In other dances the connection involves body contact. Glossary of partner dance terms Group dance – dance danced by a group of people simultaneously. Group dances are generally, but not always, coordinated or standardized in such a way that all the individuals in the group are dancing the same steps at the same time. Alternatively, various groups within the larger group may be dancing different, but complementary, parts of the larger dance. === Dance styles by main purpose === Ceremonial dance – Competitive dance – Erotic dance – Participation dance – Performance dance – Social dance – Concert dance – == Geography of dance (by region) == Africa West Africa Benin • Burkina Faso • Cape Verde • Côte dIvoire • Gambia • Ghana • Guinea • Guinea-Bissau • Liberia • Mali • Mauritania • Niger • Nigeria • Senegal • Sierra Leone • Togo North Africa Algeria • Egypt (Ancient Egypt) • Libya • Mauritania • Morocco • Sudan • South Sudan •Tunisia • Western Sahara Central Africa Angola • Burundi • Cameroon • Central African Republic • Chad • The Democratic Republic of the Congo • Equatorial Guinea • Gabon • Republic of the Congo • Rwanda • São Tomé and Príncipe East Africa Burundi • Comoros • Djibouti • Eritrea • Ethiopia • Kenya • Madagascar • Malawi • Mauritius • Mozambique • Rwanda • Seychelles • Somalia • Tanzania • Uganda • Zambia • Zimbabwe Southern Africa Botswana • Eswatini • Lesotho • Namibia • South Africa Dependencies Mayotte (France) • St. Helena (UK) • Puntland • Somaliland • Sahrawi Arab Democratic Republic Antarctica None Asia Central Asia Kazakhstan • Kyrgyzstan • Tajikistan • Turkmenistan • Uzbekistan East Asia China Tibet Hong Kong • Macau Japan • North Korea • South Korea • Mongolia • Taiwan North Asia Russia Southeast Asia Brunei • Burma (Myanmar) • Cambodia • East Timor (Timor-Leste) • Indonesia • Laos • Malaysia • Philippines • Singapore • Thailand • Vietnam South Asia Afghanistan • Bangladesh • Bhutan • Iran • Maldives • Nepal • Pakistan • Sri Lanka India West Asia Armenia • Azerbaijan • Bahrain • Cyprus (including disputed Northern Cyprus) • Georgia • Iraq • Israel • Jordan • Kuwait • Lebanon • Oman • Palestinian territories Qatar • Saudi Arabia • Syria • Turkey • United Arab Emirates • Yemen Caucasus (a region considered to be in both Asia and Europe, or between them) North Caucasus Parts of Russia (Chechnya, Ingushetia, Dagestan, Adyghea, Kabardino-Balkaria, Karachai-Cherkessia, North Ossetia, Krasnodar Krai, Stavropol Krai) South Caucasus Georgia (including disputed Abkhazia, South Ossetia) • Armenia • Azerbaijan (including disputed Nagorno-Karabakh Republic) Europe Akrotiri and Dhekelia • Åland • Albania • Andorra • Armenia • Austria • Azerbaijan • Belarus • Belgium • Bosnia and Herzegovina • Bulgaria • Croatia • Cyprus • Czech Republic • Denmark • Estonia • Faroe Islands • Finland • France • Georgia • Germany • Gibraltar • Greece • Guernsey • Hungary • Iceland • Ireland • Isle of Man • Italy • Jersey • Kazakhstan • Kosovo • Latvia • Liechtenstein • Lithuania • Luxembourg • Macedonia • Malta • Moldova (including disputed Transnistria) • Monaco • Montenegro • Netherlands • Poland • Portugal • Romania • Russia • San Marino • Serbia • Slovakia • Slovenia • Norway Svalbard Spain Autonomous communities of Spain: Catalonia Sweden • Switzerland • Turkey • Ukraine United Kingdom England • Northern Ireland • Scotland • Wales Vatican City European Union North America Canada Provinces of Canada: • Alberta • British Columbia • Manitoba • New Brunswick • Newfoundland and Labrador • Nova Scotia • Ontario (Toronto) • Prince Edward Island • Quebec • Saskatchewan Territories of Canada: Northwest Territories • Nunavut • Yukon Greenland • Saint Pierre and Miquelon United States Mexico Central America Belize • Costa Rica • El Salvador • Guatemala • Honduras • Nicaragua • Panama Caribbean Anguilla • Antigua and Barbuda • Aruba • Bahamas • Barbados • Bermuda • British Virgin Islands • Cayman Islands • Cuba • Dominica • Dominican Republic • Grenada • Haiti • Jamaica • Montserrat • Netherlands Antilles • Puerto Rico • Saint Barthélemy • Saint Kitts and Nevis • Saint Lucia • Saint Martin • Saint Vincent and the Grenadines • Trinidad and Tobago • Turks and Caicos Islands • United States Virgin Islands Oceania (includes the continent of Australia) Australasia Australia Dependencies/Territories of Australia Christmas Island • Cocos (Keeling) Islands • Norfolk Island New Zealand Melanesia Fiji • Indonesia (Oceanian part only) • New Caledonia (France) • Papua New Guinea • Rotuma • Solomon Islands • Vanuatu Micronesia Federated States of Micronesia • Guam (United States) • Kiribati • Marshall Islands • Nauru • Northern Mariana Islands (United States) • Palau • Wake Island (United States) Polynesia American Samoa (United States) • Chatham Islands (NZ) • Cook Islands (NZ) • Easter Island (Chile) • French Polynesia (France) • Hawaii (United States) • Loyalty Islands (France) • Niue (NZ) • Pitcairn Islands (UK) • Adamstown • Samoa • Tokelau (NZ) • Tonga • Tuvalu • Wallis and Futuna (France) South America Argentina • Bolivia • Brazil • Chile • Colombia • Ecuador • Falkland Islands • Guyana • Paraguay • Peru • Suriname • Uruguay • Venezuela South Atlantic Ascension Island • Saint Helena • Tristan da Cunha == History of dance == History of dance Dance in ancient Egypt Dance in mythology and religion Dance styles throughout history Medieval dance Masque English country dance Baroque dance Renaissance dance Regency dance Vintage dance Historical dance Modern dance Contemporary dance == Dance technique == Choreography Dance notation Connection Dance moves Glossary of dance moves Dance partnering Dance theory Lead and follow Musicality == Dance culture == Dance and health Dance competition Dance costume Dance critique Dance education Dance studio Dance etiquette Dance in film Dance double Dance film Dance marathon Dance music Dance party Ball (dance party) Prom Rave Dance radio Dance troupe Dance on television Nightclub Performance Performance surface (dance floor) Physically integrated dance (disability and dance) Women in dance == Dance science == Dance science Dance history – (see History of dance, above) Dance and health Dance theory Dance technology Ethnochoreology (dance anthropology) == Dance organizations == List of dance organizations == Dance-related media == Dance film Dance music Musical film === Books about dance === List of dance wikibooks == Dancers == List of dancers List of dance personalities == See also == Index of dance articles Outline of music Music Musical terminology International folk dance Quotations about dance == External links == Historic Illustrations of Dancing from 3300 B.C. to 1911 A.D. from Project Gutenberg United States National Museum of Dance and Hall of Fame"
    
    content = "A home is a permanent or semi-permanent residence for individuals or families, often including pets. It serves various domestic functions, such as sleeping and cooking, and can take many forms: traditional houses, mobile structures like trailers, or even digital spaces. The concept of home encompasses emotional aspects like belonging and identity, evolving from natural shelters to constructed dwellings throughout history. Homes reflect cultural and personal meanings, influencing perceptions of security and socialization. Additionally, the relationship between home and homelessness highlights its significance in understanding human existence, as the notion of home can vary greatly across different cultures and individual experiences"
    
    similarity = evaluate_similarity(original_content, content)
    print(similarity)
    
    
    
    
    
    
    
    
    
    
    