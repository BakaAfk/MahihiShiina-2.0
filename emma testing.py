from typing import cast
from enma import Enma, Sources, CloudFlareConfig, NHentai

enma = Enma[Sources]() # or just Enma()

config = CloudFlareConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    cf_clearance=''
)

enma.source_manager.set_source(source_name=Sources.NHENTAI)
nh_source = cast(NHentai, enma.source_manager.source)
nh_source.set_config(config=config)

doujin = enma.random()
print(doujin)