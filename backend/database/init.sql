/* Disclaimer: this is mock data. It should not be relied upon to determine any property’s safety or compliance with the soft story program.*/

-- Create PostGIS extension
create extension if not exists postgis;

set search_path to public;

create table if not exists liquefaction_zones (
    identifier varchar(255) primary key,
    geometry Geometry(multipolygon, 4326) not null,
    liq varchar(255),
    shape_length float,
    shape_area float,
    update_timestamp timestamp
);

create table if not exists landslide_zones (
    identifier integer primary key,
    geometry Geometry(multipolygon, 4326) not null,
    gridcode integer,
    sum_shape float,
    shape_length float,
    shape_length_1 float,
    shape_area float,
    update_timestamp timestamp
);

create table if not exists tsunami_zones (
    identifier integer primary key,
    evacuate varchar(255) not null,
    county varchar(255) not null,
    global_id varchar(255) not null,
    shape_length float,
    shape_area float,
    geometry Geometry(multipolygon, 4326) not null,
    update_timestamp timestamp
);

create table if not exists soft_story_properties (
    identifier integer not null,
    block varchar(255),
    lot varchar(255),
    parcel_number varchar(255),
    property_address varchar(255),
    address varchar(255) not null,
    tier integer,
    status varchar(255),
    bos_district integer,
    point Geometry(point, 4326),
    sfdata_as_of timestamp,
    sfdata_loaded_at timestamp,
    update_timestamp timestamp,
    point_source varchar(255)
);

insert into landslide_zones (
    identifier, geometry, gridcode, sum_shape, shape_length, shape_area, update_timestamp
) values
    (3, ST_GeomFromText('MULTIPOLYGON(
        ((-122.5 37.7, -121.9 30.7, -122.4 37.8, -122.5 37.8, -122.5 37.7)),
        ((-122.6 37.6, -121.5 37.6, -122.5 37.7, -122.6 37.7, -122.6 37.6))
    )', 4326), 8, 1000.00, 25.8, 12.0, '2024-12-10 20:20:00'),

    (4, ST_GeomFromText('MULTIPOLYGON(
        ((-122.5 37.7, -122.5 37.9, -122.3 37.9, -122.3 37.7, -122.5 37.7)),
        ((-122.4 37.75, -122.4 37.85, -122.35 37.85, -122.35 37.75, -122.4 37.75))
    )', 4326), 3, 897.6, 12.2, 87.0, '2024-12-10 13:15:00'),

    (5, ST_GeomFromText('MULTIPOLYGON(
        ((-122.5 37.7, -122.5 37.8, -122.4 37.8, -122.4 37.7, -122.5 37.7)),
        ((-122.48 37.73, -122.48 37.77, -122.46 37.77, -122.46 37.73, -122.48 37.73))
    )', 4326), 10, 56.11, 18.3, 43.1, '2024-12-10 13:15:00');                         

insert into liquefaction_zones (identifier, geometry, liq, shape_length, shape_area, update_timestamp) values 
                                ('6', ST_GeomFromText('MULTIPOLYGON(
                                        ((-121.0 37.6, -121.9 30.7, -122.4 37.8, -122.5 37.8, -121.0 37.6)),
                                        ((-123.1 33.6, -121.5 37.6, -122.5 37.7, -122.6 37.7, -123.1 33.6))
                                    )', 4326), 
                                'H', 25.8, 12.0, '2024/12/19 8:20:00 PM'),

                                ('7', ST_GeomFromText('MULTIPOLYGON(
                                        ((-125.9 37.8, -121.3 37.8, -122.35 37.85, -125.9 37.8)),
                                        ((-122.5 37.7, -129.4 37.7, -122.4 37.8, -122.5 37.8, -122.5 37.7))
                                    )', 4326), 
                                'VH', 12.2, 87.0, '2024/12/19 1:15:00 PM'),
                                ('8', ST_GeomFromText('MULTIPOLYGON(
                                        ((-123.9 37.8, -123.3 37.8, -122.35 37.85, -123.9 37.8)),
                                        ((-124.0 27.9, -127.4 37.7, -122.4 37.8, -122.5 37.8, -124.0 27.9))
                                    )', 4326), 
                                'H', 123.4, 432.1, '2024/12/19 1:15:00 PM')                                
                                ;

insert into tsunami_zones (identifier, evacuate, county, global_id, shape_length, shape_area, geometry, update_timestamp) values 
                                (9, 'Yes, Tsunami Hazard Area', 'San Francisco', 'd63b7111-a144-49ca-aa79-69f69721e3d3', 123.45, 67.8, ST_GeomFromText('MULTIPOLYGON(
                                    ((-122.5 37.7, -122.5 37.9, -122.3 37.9, -122.3 37.7, -122.5 37.7)),
                                    ((-122.4 37.75, -122.4 37.85, -122.35 37.85, -122.35 37.75, -122.4 37.75))
                                )', 4326), 
                                '2024/12/16 5:10:00 PM');                                

--add update_timestamp column after sfdata_loaded_at
--this column will be filled with data generated at runtime by our code

--status column is a varchar in the database but must be transformed into a boolean for use
--possibly keep the booleans in the transformed database in memory between updates

--point of address 6 is available in MapBox, but we kept the SFData coordinates

insert into soft_story_properties (identifier, block, lot, parcel_number, property_address, address,                            tier, status,                      bos_district, point,                                                        sfdata_as_of,             sfdata_loaded_at,         update_timestamp,        point_source) values
                                  (1,          3578,  71,  3578071,       '3549 17TH ST',   '3549 17TH ST, SAN FRANCISCO CA',   3,    'Work Complete, CFC Issued', 8,            ST_SetSRID(ST_MakePoint(-122.424968, 37.76293), 4326),        '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'mapbox'),
                                  (2,          41,    4,   41004,         '2231 POWELL ST', '2231 POWELL ST, SAN FRANCISCO CA', 3,    'Non-Compliant',             3,            ST_SetSRID(ST_MakePoint(-122.41211, 37.80541), 4326),         '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'mapbox'),
                                  (3,          1896,  46,  1896046,       '1612 48TH AV',   '1612 48TH AV, SAN FRANCISCO CA',   3,    'Work Complete, CFC Issued', 4,            ST_SetSRID(ST_MakePoint(-122.507458, 37.756332), 4326),       '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'mapbox'),
                                  (4,          1222,  55,  1222055,       '253 CENTRAL AV', '253 CENTRAL AV, SAN FRANCISCO CA', 3,    'Work Complete, CFC Issued', 5,            ST_SetSRID(ST_MakePoint(-122.443866, 37.771451), 4326),       '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'mapbox'),
                                  (5,          1730,  49,  1730049,       '1240 21ST AV',   '1240 21ST AV, SAN FRANCISCO CA',   3,    'Work Complete, CFC Issued', 4,            ST_SetSRID(ST_MakePoint(-122.479011, 37.764539), 4326),       '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'mapbox'),
                                  (6,          4217,  12,  4217012,       '2120 24TH ST',   '2120 24TH ST, SAN FRANCISCO CA',   3,    'Work Complete, CFC Issued', 10,           ST_SetSRID(ST_MakePoint(-122.400877183, 37.753556427), 4326), '2024/11/04 03:18:13 AM', '2024/11/04 03:30:26 AM', '2024/11/28 5:11:26 PM', 'sfdata');
                                