# tvh-picon-check
Container to be used after making use of picons/picons respository to generate TvHeadend server icons

Example Docker Compose:

```
tvh-picon-check:
    image: harminderdhak/tvh-picon-check:latest
    container_name: tvh-picon-check
    ports:
      - "9986:9986"  # Change the host port if needed. 9986 is default port in the script
    volumes:
      - ./servicelist-tvheadend-servermode-srp.txt:/data/servicelist.txt:ro #path to where srp.txt is created/moved to
      - ./picons:/data/picons:ro # location where picons are saved, after creation by picons/picons
    environment:
      SRP_FILE: /data/servicelist.txt
      PICON_DIR: /data/picons
      ICON_AUTH_CODE: PxMJQzcACRaT5VT3bUUkpzVBtsbE # user with access to channels that require icons
    restart: always
```    
