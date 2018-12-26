--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6 (Ubuntu 10.6-1.pgdg14.04+1)
-- Dumped by pg_dump version 10.3

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_with_oids = false;

--
-- Name: cache_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE cache_data (
    _id bigint NOT NULL,
    type text NOT NULL,
    value text
);


--
-- Name: cache_data__id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE cache_data__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cache_data__id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE cache_data__id_seq OWNED BY cache_data._id;


--
-- Name: server_backgrounds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE server_backgrounds (
    _id bigint NOT NULL,
    server_id text NOT NULL,
    background_url text,
    background_type text
);


--
-- Name: server_backgrounds__id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE server_backgrounds__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: server_backgrounds__id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE server_backgrounds__id_seq OWNED BY server_backgrounds._id;


--
-- Name: server_channels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE server_channels (
    _id bigint NOT NULL,
    server_id text NOT NULL,
    channel_type text NOT NULL,
    channel_id text
);


--
-- Name: server_channels__id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE server_channels__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: server_channels__id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE server_channels__id_seq OWNED BY server_channels._id;


--
-- Name: server_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE server_data (
    _id bigint NOT NULL,
    server_id text NOT NULL,
    server_name text,
    last_help_msg text,
    last_help_channel text,
    next_shop integer,
    latest_shop text,
    prefix text DEFAULT '.rb'::text,
    last_status_msg text,
    last_status_channel text,
    priority smallint,
    premium boolean DEFAULT false,
    locale text DEFAULT 'en'::text,
    last_seen integer
);


--
-- Name: server_data__id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE server_data__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: server_data__id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE server_data__id_seq OWNED BY server_data._id;


--
-- Name: user_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE user_links (
    _id integer NOT NULL,
    user_id text,
    user_nickname text,
    user_platform text
);


--
-- Name: user_links__id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE user_links ALTER COLUMN _id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME user_links__id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: cache_data _id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY cache_data ALTER COLUMN _id SET DEFAULT nextval('cache_data__id_seq'::regclass);


--
-- Name: server_backgrounds _id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_backgrounds ALTER COLUMN _id SET DEFAULT nextval('server_backgrounds__id_seq'::regclass);


--
-- Name: server_channels _id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_channels ALTER COLUMN _id SET DEFAULT nextval('server_channels__id_seq'::regclass);


--
-- Name: server_data _id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_data ALTER COLUMN _id SET DEFAULT nextval('server_data__id_seq'::regclass);


--
-- Name: cache_data cache_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY cache_data
    ADD CONSTRAINT cache_data_pkey PRIMARY KEY (_id);


--
-- Name: server_backgrounds server_backgrounds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_backgrounds
    ADD CONSTRAINT server_backgrounds_pkey PRIMARY KEY (_id);


--
-- Name: server_channels server_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_channels
    ADD CONSTRAINT server_channels_pkey PRIMARY KEY (_id);


--
-- Name: server_data server_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_data
    ADD CONSTRAINT server_data_pkey PRIMARY KEY (_id);


--
-- Name: server_data server_data_server_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY server_data
    ADD CONSTRAINT server_data_server_id_key UNIQUE (server_id);


--
-- Name: user_links user_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_links
    ADD CONSTRAINT user_links_pkey PRIMARY KEY (_id);


--
-- Name: user_links user_links_user_id_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_links
    ADD CONSTRAINT user_links_user_id_unique UNIQUE (user_id);


--
-- PostgreSQL database dump complete
--