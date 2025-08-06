# tvh-picon-check
Container to be used after making use of picons/picons respository to generate icons, for TVHeadend Server.

The container will retrieve a channel list from TVHeadend server, using persistent password from ICON_AUTH_CODE. This list will then be compared with srp.txt file and picons generated.

A Web server will return if any picons have been generated, for each Channel on the TVHeadend server. This is presentated in a tabular format.

All channels missing a picon match and picon can be seen by a toggle. A list can be generated of all the channels that failed to match during the srp.txt creation, ready to be raised as an issue for missing srp references. You will need to manually match the missing channels. After manually matching the channels, these can be added to the srp.index and tested, before being raised as an Issue on picons/picons.

Example Docker Compose:

```
tvh-picon-check:
    image: harrysingh1991/tvh-picon-check:latest
    container_name: tvh-picon-check
    ports:
      - "9986:9986"  # Change the host port if needed. 9986 is default port in the script
    volumes:
      - ./servicelist-tvheadend-servermode-srp.txt:/app/servicelist.txt:ro #path to where srp.txt can be accessed
      - ./picons:/app/picons:ro # location where picons are saved, after creation/moved to
    environment:
      ICON_AUTH_CODE: PersistentPasswordGoesHere # user with access to channels that require icons
    restart: always
```    
