create table if not exists test (
   test_id serial primary key,
   name    varchar(255)
);

create table if not exists season (
   season_id serial primary key,
   name      varchar(20) not null unique,
      check ( name in ( 'spring',
                        'summer',
                        'autumn',
                        'winter' ) )
);

insert into season ( name ) values ( 'spring' ),( 'summer' ),( 'autumn' ),( 'winter' );

create table if not exists weather (
   weather_id serial primary key,
   name       varchar(50) not null unique,
      check ( name in ( 'sunny',
                        'rainy',
                        'cloudy',
                        'windy' ) )
);

insert into weather ( name ) values ( 'sunny' ),( 'rainy' ),( 'cloudy' ),( 'windy' );

create table if not exists cities (
   city_id serial primary key,
   name    varchar(40) not null unique
);

create table if not exists neighborhood (
   neighborhood_id serial primary key,
   city_id         int not null
      references city ( city_id )
         on delete cascade,
   name            varchar(50) not null,
   unique ( city_id,
            name )
);


create table if not exists image (
   image_id        serial primary key,
   file_path       text,          -- oder URL
   date_taken      timestamp with time zone,
   season_id       int
      references season ( season_id ),
   city_id         int
      references city ( city_id ),
   neighborhood_id int
      references neighborhood ( neighborhood_id ),
   unique ( file_path ) -- ???? soll so beleiben???
);

create table if not exists starterkit (
   starterkit_id   serial primary key,
   name            varchar(200),
   source_image_id int
      references image ( image_id ),  -- Bild, aus dem die Items extrahiert wurden
   year            int,                             -- optional redundante Kopie (für schnelle Filter)
   season_id       int
      references season ( season_id ),
   weather_id      int
      references weather ( weather_id )
);



create table if not exists clothing_category (
   clothing_category_id serial primary key,
   subtype_id           int,
   name                 varchar(100) not null unique check ( name in ( 'shoes',
                                                       'bottoms',
                                                       'tops',
                                                       'outerwear',
                                                       'accessoires',
                                                       'animals' ) )
);

insert into clothing_category ( name ) values ( 'shoes',
                                                'bottoms',
                                                'tops',
                                                'outerwear',
                                                'accessoires',
                                                'animals' );

create table if not exists subtype (
   subtype_id           serial primary key,
   clothing_category_id int
      references clothing_category ( clothing_category_id ),
   subtype              varchar(30),
      check ( subtype in ( 'shirtless',
                           'long sleeve',
                           't-shirt',
                           'top',
                           'blouse',
                           'denim jacket',
                           'cardigan',
                           'rain coat',
                           'winter coat',
                           'shorts',
                           'skirt',
                           'jeans',
                           'leggings',
                           'shorts',
                           'skirt',
                           'jeans',
                           'leggings',
                           'boots',
                           'heels',
                           'flipflop',
                           'sneaker',
                           'sandals',
                           'cat',
                           'dog',
                           'other' ) )
);

create table if not exists person_detection (
   person_detection_id serial primary key,
   image_id            int not null
      references image ( image_id )
         on delete cascade,
   bbox_x              float,
   bbox_y              float,
   bbox_w              float,
   bbox_h              float,
   confidence          float --- check if datapoints are valid within pipline
);

create table if not exists image_person (
   person_detection_id int not null
      references person_detection ( person_detection_id )
         on delete cascade,
   image_id            int not null
      references image ( image_id )
         on delete cascade,
   primary key ( person_detection_id,
                 image_id )
);


create table if not exists subtype_clothing_category (
   subtype_id           int primary key, -- PROBLEM: PK-FK bezeihung muss hier passen: was refenzeirt wen? ich kann nicht hier references und dann FK von 6 subtypoe tabellen machen...
   clothing_category_id int
      references clothing_category ( clothing_category_id )
);

create table if not exists clothing_item (
   clothing_item_id     int primary key,
   person_detection_id  int
      references person_detection ( person_detection_id ),
   clothing_category_id int
      references clothing_category ( clothing_category_id ),
   subtype_id           int
      references subtype_clothing_category ( clothing_category_id ),
   colour               varchar(25)
);


create table if not exists starterkit_item (
   starterkit_item_id int primary key,
   starterkit_id      int not null
      references starterkit ( starterkit_id )
         on delete cascade,
   clothing_item_id   int not null
      references clothing_item ( clothing_item_id )
         on delete cascade,
   primary key ( starterkit_id,
                 clothing_item_id )
);


create table if not exists mapillary_detections (
   id                    serial primary key,
   cropped_file          varchar(255) not null,
   original_image_id     bigint not null,
   captured_at           datetime,
   location              text,
   bounding_box_original text,
   created_at            datetime default current_timestamp,
   city_id               integer
      references cities ( id )
         on delete set null
);








/*

create table if not exists subtype_top (
   subcategory_id serial primary key,
   top_type       varchar(20) not null unique check ( top_type in ( 'shirtless',
                                                              'long sleeve',
                                                              't-shirt',
                                                              'top',
                                                              'blouse' ) )
);
create table if not exists subtype_outerwear (
   subcategory_id serial primary key,
   outerwear_type varchar(20) not null unique check ( outerwear_type in ( 'denim jacket',
                                                                          'cardigan',
                                                                          'rain coat',
                                                                          'winter coat' ) )
);

create table if not exists subtype_bottoms (
   subcategory_id serial primary key,
   bottoms_type   varchar(20) not null unique check ( bottoms_type in ( 'shorts',
                                                                      'skirt',
                                                                      'jeans',
                                                                      'leggings' ) )
);

create table if not exists subtype_accessoires (
   subcategory_id serial primary key,
   bottoms_type   varchar(20) not null unique check ( bottoms_type in ( 'shorts',
                                                                      'skirt',
                                                                      'jeans',
                                                                      'leggings' ) )
);

create table if not exists subtype_shoes (
   subcategory_id serial primary key,
   bottoms_type   varchar(20) not null unique check ( bottoms_type in ( 'boots',
                                                                      'heels',
                                                                      'flipflop',
                                                                      'sneaker',
                                                                      'sandals' ) )
);

create table if not exists subtype_animals (
   subcategory_id serial primary key,
   bottoms_type   varchar(20) not null unique check ( bottoms_type in ( 'cat',
                                                                      'dog',
                                                                      'other' ) )
);

*/