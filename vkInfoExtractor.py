import vk
import gzip
import json
import json_lines

class vkExtractor:
    def __init__(self):
        session = vk.Session()
        self.vkapi = vk.API(session)
        self.fields='photo_id,verified,sex,bdate,career,city,contacts,counters,country,education,exports,home_town,has_photo,photo_50,photo_100,photo_200_orig,photo_200,photo_400_orig,photo_max,photo_max_orig,online,domain,has_mobile,site,universities,schools,status,last_seen,followers_count,occupation,nickname,relatives,relation,personal,connections,wall_comments,activities,interests,music,movies,tv,books,games,about,quotes,can_post,can_see_all_posts,can_see_audio,can_write_private_message,can_send_friend_request,is_favorite,is_hidden_from_feed,timezone,screen_name,maiden_name,crop_photo,is_friend,friend_status,military,blacklisted,blacklisted_by_me'

    def extract_info(self, user_Id = 1, fields = fields):
        user = vkapi('users.get',user_id=user_Id, extent=1,fields=fields)
        friends = vkapi('friends.get',user_id=user_Id,fields=fields)
        followers = vkapi('users.getFollowers',user_id=user_Id,fields=fields)
        subscriptions = vkapi('users.getSubscriptions',user_id=user_Id, extended=1,fields=fields)
        wallphotos = vkapi('photos.get',owner_id=user_Id, album_id='wall', extended=1)
        profilephotos = vkapi('photos.get',owner_id=user_Id, album_id='profile', extended=1)
        data=[{'user': user[0]}, {'friends':friends},{'followers': followers},{'subscriptions': subscriptions},{'wallphotos':wallphotos}, {'profilephotos':profilephotos}]
        self.entity_ids={'country':[],'city':[]}
        self.entities={'country':{},'city':{}}
        self.database_entities=['country', 'city']
        self.collect_entity_ids(data)
        self.get_from_api()
        self.fill_in_entities(data)
        return data

    def write_jl(self, path, data, mode='w'):
        with open(str(path), mode) as f:
            f.write(self.jl(data))

    def write_gz(self, path, data, mode='wb'):
        with gzip.open(str(path), mode) as f:
            f.write(data)

    def write_jl_gz(self, path, data, mode='wb'):
        write_gz(path, data=self.jl_bytes(data), mode=mode)

    def jl_bytes(self, data):
        return '\n'.join(json.dumps(x) for x in data).encode('utf8')

    def jl(self, data):
        return '\n'.join(json.dumps(x) for x in data)

    def read_jl_gz(self, path):
        with gzip.open(path, 'rb') as f:
            return list(json_lines.reader(f))

    def read_jl(self, path):
        with json_lines.open(path) as f:
            return list(f)

    def collect_entity_ids(self, obj):
        if (type(obj) is dict):
            for entity in self.database_entities:
                if entity in obj and obj[entity] not in self.entity_ids[entity]:
                    self.entity_ids[entity].append(obj[entity])
            for item in obj:
                if (type(obj[item]) is list):
                    for nested_obj in obj[item]:
                        self.collect_entity_ids(nested_obj)
                if (type(obj[item]) is dict):
                    self.collect_entity_ids(obj[item])
        if (type(obj) is list):
            for nested_obj in obj:
                self.collect_entity_ids(nested_obj)

    def fill_in_entities(self, obj):
        if (type(obj) is dict):
            for entity in self.database_entities:
                if entity in obj and obj[entity] in self.entity_ids[entity] and entity + '_name' not in obj and obj[entity] in self.entities[entity]:
                    obj[entity + '_name'] = self.entities[entity][obj[entity]]
            for item in obj:
                if (type(obj[item]) is list):
                    for nested_obj in obj[item]:
                        self.fill_in_entities(nested_obj)
                if (type(obj[item]) is dict):
                    self.fill_in_entities(obj[item])
        if (type(obj) is list):
            for nested_obj in obj:
                self.fill_in_entities(nested_obj)

    def get_from_api(self):
        cities = vkapi('database.getCitiesById',city_ids=self.entity_ids['city'])
        for city in cities:
            self.entities['city'][city['cid']]=city['name']
        countries = vkapi('database.getCountriesById',country_ids=self.entity_ids['country'])
        for country in countries:
            self.entities['country'][country['cid']]=country['name']