--
-- PostgreSQL database dump
--

\restrict DXb3MLM6N9bpYGQ91NSpjcCqwSlihZqaYTYbVEPHguSmhHdEFwPPe7SGX9jnFFg

-- Dumped from database version 16.10 (Debian 16.10-1.pgdg13+1)
-- Dumped by pg_dump version 16.10 (Debian 16.10-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: manuscriptstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.manuscriptstatus AS ENUM (
    'SUBMITTED',
    'RE_SUBMITTED',
    'UNDER_REVIEW',
    'REVISED',
    'ACCEPTED',
    'REJECTED',
    'REVISION_REQUESTED',
    'PUBLISHED'
);


ALTER TYPE public.manuscriptstatus OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    country_id integer NOT NULL
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- Name: cities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cities_id_seq OWNER TO postgres;

--
-- Name: cities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cities_id_seq OWNED BY public.cities.id;


--
-- Name: countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.countries (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(10)
);


ALTER TABLE public.countries OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.countries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.countries_id_seq OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.countries_id_seq OWNED BY public.countries.id;


--
-- Name: languages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.languages (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    code character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.languages OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.languages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.languages_id_seq OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.languages_id_seq OWNED BY public.languages.id;


--
-- Name: manuscript_annotations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manuscript_annotations (
    id character varying(255) NOT NULL,
    manuscript_id integer NOT NULL,
    evaluator_id integer NOT NULL,
    annotation_type character varying(20) NOT NULL,
    page_number integer NOT NULL,
    x_position double precision NOT NULL,
    y_position double precision NOT NULL,
    position_data text NOT NULL,
    comment text NOT NULL,
    content_data text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT check_annotation_type CHECK (((annotation_type)::text = ANY ((ARRAY['text'::character varying, 'area'::character varying, 'freetext'::character varying])::text[]))),
    CONSTRAINT check_page_number_positive CHECK ((page_number >= 1))
);


ALTER TABLE public.manuscript_annotations OWNER TO postgres;

--
-- Name: manuscript_evaluation_grids; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manuscript_evaluation_grids (
    id integer NOT NULL,
    manuscript_id integer NOT NULL,
    evaluator_id integer NOT NULL,
    originality_of_ideas text NOT NULL,
    methodology_rigor text NOT NULL,
    theoretical_approach text NOT NULL,
    presentation_clarity text NOT NULL,
    strengths text NOT NULL,
    weaknesses text NOT NULL,
    suggestions text,
    recommendation character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    submitted_at timestamp with time zone
);


ALTER TABLE public.manuscript_evaluation_grids OWNER TO postgres;

--
-- Name: manuscript_evaluation_grids_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.manuscript_evaluation_grids_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.manuscript_evaluation_grids_id_seq OWNER TO postgres;

--
-- Name: manuscript_evaluation_grids_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.manuscript_evaluation_grids_id_seq OWNED BY public.manuscript_evaluation_grids.id;


--
-- Name: manuscript_evaluators; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manuscript_evaluators (
    manuscript_id integer NOT NULL,
    evaluator_id integer NOT NULL,
    assigned_by_id integer NOT NULL,
    assigned_at timestamp without time zone NOT NULL,
    status character varying(8) NOT NULL,
    response_at timestamp without time zone,
    evaluation_deadline timestamp without time zone,
    CONSTRAINT evaluatorassignmentstatus CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'ACCEPTED'::character varying, 'DECLINED'::character varying])::text[])))
);


ALTER TABLE public.manuscript_evaluators OWNER TO postgres;

--
-- Name: manuscripts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manuscripts (
    id integer NOT NULL,
    title character varying(500) NOT NULL,
    abstract character varying,
    keywords character varying,
    author_id integer NOT NULL,
    theme_id integer,
    section_id integer NOT NULL,
    language_id integer NOT NULL,
    status public.manuscriptstatus NOT NULL,
    pdf_filename character varying(255) NOT NULL,
    last_revision_at timestamp without time zone,
    decision_at timestamp without time zone,
    published_at timestamp without time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.manuscripts OWNER TO postgres;

--
-- Name: manuscripts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.manuscripts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.manuscripts_id_seq OWNER TO postgres;

--
-- Name: manuscripts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.manuscripts_id_seq OWNED BY public.manuscripts.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    signe_min integer NOT NULL,
    signe_max integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT check_signe_max_gt_min CHECK ((signe_max > signe_min))
);


ALTER TABLE public.sections OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_id_seq OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: themes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.themes (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.themes OWNER TO postgres;

--
-- Name: themes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.themes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.themes_id_seq OWNER TO postgres;

--
-- Name: themes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.themes_id_seq OWNED BY public.themes.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_by integer,
    assigned_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO postgres;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    email_verified boolean NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(150) NOT NULL,
    profile_photo character varying(255),
    orcid_id character varying(50),
    is_active boolean NOT NULL,
    bio character varying,
    "position" character varying,
    institution character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: cities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities ALTER COLUMN id SET DEFAULT nextval('public.cities_id_seq'::regclass);


--
-- Name: countries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries ALTER COLUMN id SET DEFAULT nextval('public.countries_id_seq'::regclass);


--
-- Name: languages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.languages ALTER COLUMN id SET DEFAULT nextval('public.languages_id_seq'::regclass);


--
-- Name: manuscript_evaluation_grids id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluation_grids ALTER COLUMN id SET DEFAULT nextval('public.manuscript_evaluation_grids_id_seq'::regclass);


--
-- Name: manuscripts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts ALTER COLUMN id SET DEFAULT nextval('public.manuscripts_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: themes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes ALTER COLUMN id SET DEFAULT nextval('public.themes_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20251224_add_evaluation_grids
\.


--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cities (id, name, country_id) FROM stdin;
\.


--
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.countries (id, name, code) FROM stdin;
\.


--
-- Data for Name: languages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.languages (id, name, code, created_at, updated_at) FROM stdin;
1	Français	fr	2025-12-24 16:30:44.567591+00	2025-12-24 16:30:44.567593+00
2	Anglais	an	2025-12-24 21:43:07.365476+00	2025-12-24 21:43:07.365478+00
\.


--
-- Data for Name: manuscript_annotations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manuscript_annotations (id, manuscript_id, evaluator_id, annotation_type, page_number, x_position, y_position, position_data, comment, content_data, created_at, updated_at) FROM stdin;
0811f8e7-c265-48e7-af80-ba6f2c63d708	2	7	text	1	146.4375	402.7421875	{"boundingRect":{"x1":146.4375,"y1":402.7421875,"x2":456.2808837890625,"y2":501.9453125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},"rects":[{"x1":146.4375,"y1":402.7421875,"x2":456.2808837890625,"y2":422.2421875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":422.6640625,"x2":452.657470703125,"y2":442.1640625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":442.59375,"x2":453.53466796875,"y2":462.09375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":462.515625,"x2":456.275634765625,"y2":482.015625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":482.4453125,"x2":310.634033203125,"y2":501.9453125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1}]}	changer sa	{"text":"Recent advances in multimodal LLMs and sys- tems that use tools for long-video QA point to the promise of reasoning over hour-long episodes. However, many methods still com- press content into lossy "}	2025-12-24 22:07:14.662794+00	2025-12-24 22:07:14.662826+00
ff618c90-119b-4039-bc5c-c23ae043a421	2	7	text	2	117.5625	233.2421875	{"boundingRect":{"x1":117.5625,"y1":233.2421875,"x2":484.9483642578125,"y2":479.5078125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},"rects":[{"x1":136.41156005859375,"y1":233.2421875,"x2":481.56243896484375,"y2":253.7421875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":255.8359375,"x2":481.884033203125,"y2":276.3359375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":117.5625,"y1":278.421875,"x2":484.9483642578125,"y2":298.921875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":301.015625,"x2":484.855224609375,"y2":321.515625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":323.609375,"x2":482.48187255859375,"y2":344.109375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":346.1953125,"x2":484.86932373046875,"y2":366.6953125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":368.7890625,"x2":484.871826171875,"y2":389.2890625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":391.375,"x2":484.86773681640625,"y2":411.875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":413.828125,"x2":481.56280517578125,"y2":434.328125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":436.421875,"x2":482.300537109375,"y2":456.921875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":459.0078125,"x2":484.8719482421875,"y2":479.5078125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2}]}	changer sa	{"text":"s demonstrated promising effectiveness. These findings highlight the potential of tool-augmented LLM agents in achieving both efficiency and accu- racy. However, the initial incarnation of VideoA- gent relies on a less powerful toolset, primarily generic vision-language foundation models for cap- tioning and image retrieval. Such tools are often in- sufficient for capturing fine-grained semantics, pre- cise object references, or subtle temporal cues. This restricts the agent’s ability to understand complex scenes and reason over long temporal spans. More-"}	2025-12-24 22:08:36.228095+00	2025-12-24 22:08:36.228113+00
a4eb4214-de46-4e42-8e2e-d2ba8ea688bd	2	2	text	1	146.4375	402.7421875	{"boundingRect":{"x1":146.4375,"y1":402.7421875,"x2":456.2808837890625,"y2":541.7890625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},"rects":[{"x1":146.4375,"y1":402.7421875,"x2":456.2808837890625,"y2":422.2421875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":422.6640625,"x2":452.657470703125,"y2":442.1640625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":442.59375,"x2":453.53466796875,"y2":462.09375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":462.515625,"x2":456.275634765625,"y2":482.015625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":482.4453125,"x2":453.52978515625,"y2":501.9453125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":502.3671875,"x2":456.27252197265625,"y2":521.8671875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},{"x1":146.4375,"y1":522.2890625,"x2":318.48175048828125,"y2":541.7890625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1}]}	a changer	{"text":"Recent advances in multimodal LLMs and sys- tems that use tools for long-video QA point to the promise of reasoning over hour-long episodes. However, many methods still com- press content into lossy summaries or rely on limited toolsets, weakening temporal ground- ing and missing fine-grai"}	2025-12-24 22:50:31.31364+00	2025-12-24 22:50:31.313733+00
91da5386-fc19-4846-baee-64b9ca83b175	2	2	area	1	515	397	{"boundingRect":{"x1":515,"y1":397,"x2":873,"y2":620,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":1},"rects":[]}	image a changer trop de pixels	{"image":"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAWYAAADfCAYAAADFlHkfAAAAAXNSR0IArs4c6QAAIABJREFUeF7sXQd8FNXXPdtbekLovffeERAsYG+ICnZF7AWx8LdX7F3sqKg0BSs2RFSUDtJLIJSE9J5sL/N95242LIFAAokkMNcfP2F2yps7b867c96952kURVGg2jF54IEHHsBPP/0kfxo0aIBRo0bhlFNOwf/+9z8MHDgQV155JW655Ra5Bv99+eWX44477sA333yDcePGYdasWTj77LMxbdo0vPrqq9i+fTvuvfdebNiwAV9//TUsFstB7evQoQOeeOIJXHrppfLbd999h1tvvRV79+6F3+9H9+7d0aNHD3z44Yf47bffMGbMGKSnp2PVqlUYOXIkHn/8cTzyyCP45JNP8NRTTyEpKemYfHC4gz/++GO53q5du2rsGtV54oKCAvH/Rx99BL4eZrMZTZs2hUajqc7LVOlcbEdKSgpcLpe04/rrr8cLL7yAmJiYKp1H3blueECjAvOxP6jevXvj5ptvxg033CAnO+eccwSACcx9+vTBhAkT5A9t8ODBuOqqq3DTTTfh2muvhU6nw3nnnYfvv/8eM2fOxD333CMgtmPHDgH4nJwcXHTRRXjuuedQr169ssZ27NhR9gsB8w8//CDnTE1Nxc8//yzgv2fPHkRGRsoxcXFx+Pbbb+H1enHuueeiqKgIWq0Ws2fPlnbyejVldQ2YP/30U9x4443weDzo27cv7rvvPvTs2VP8dbwsEAhg7dq10g84uJpMJrz33nvSl1Q78TygAnM1PNMuXbrg4YcfxtixYw8C5tNOOw0Ebr5QoYiZwDhlyhRcccUVAsbx8fE488wzcd1110k0GzKfz4c//vgDDz30EFq1aoXPP/+87LdOnTrh0UcfLbvmjz/+KFFUWlqaRN7cd8mSJbI/wb1Ro0ZYt24dsrKyBOhzc3PlNwIz284ovaasLgGz0+nEZZddJoNYs2bN5GuGg2xtsX/++UcGXX4ZnX/++dJ/DvVFVVvaq7bj6DygAvPR+e2Ao26//XahHSZPnixRFiOsa665RiJRAvKbb74p0Q3B84033sDpp5+OX375RWiG+++/H3/99Rfatm0rlAM/n99++21ceOGFGD16NO6++2689tprQnvwpQxZ586dBVAJIjRGyVdffTUyMjKwePFieWkZ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"}	2025-12-24 22:51:03.250107+00	2025-12-24 22:51:03.250123+00
2538319c-d616-4eca-837b-37abb9956b04	2	2	text	2	118.0625	820.3203125	{"boundingRect":{"x1":118.0625,"y1":820.3203125,"x2":484.1168212890625,"y2":998.953125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},"rects":[{"x1":203.4608154296875,"y1":820.3203125,"x2":482.4873046875,"y2":840.8203125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":842.9140625,"x2":481.55865478515625,"y2":863.4140625,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":865.5,"x2":481.8515625,"y2":886,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":888.09375,"x2":481.841796875,"y2":908.59375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":910.6796875,"x2":481.84033203125,"y2":931.1796875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":933.2734375,"x2":484.1168212890625,"y2":953.7734375,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":955.8671875,"x2":481.854736328125,"y2":976.3671875,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2},{"x1":118.0625,"y1":978.453125,"x2":357.41888427734375,"y2":998.953125,"width":992.1266666666666,"height":1403.1499999999999,"pageNumber":2}]}	trop de texte	{"text":"nt gathers these outputs to iteratively reason over the accumulated evidence. To guide the reasoning process, we design a reward-driven training strategy that encourages the master agent to conduct structured, multi-step reasoning. In each iteration, the master agent generates sub-queries, invokes either the grounding or vision agent as needed, and integrates the retu"}	2025-12-24 22:51:32.212868+00	2025-12-24 22:51:32.212887+00
\.


--
-- Data for Name: manuscript_evaluation_grids; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manuscript_evaluation_grids (id, manuscript_id, evaluator_id, originality_of_ideas, methodology_rigor, theoretical_approach, presentation_clarity, strengths, weaknesses, suggestions, recommendation, created_at, updated_at, submitted_at) FROM stdin;
\.


--
-- Data for Name: manuscript_evaluators; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manuscript_evaluators (manuscript_id, evaluator_id, assigned_by_id, assigned_at, status, response_at, evaluation_deadline) FROM stdin;
1	5	4	2025-12-24 16:46:01.505281	PENDING	\N	2026-01-25 15:45:00
1	2	4	2025-12-24 16:47:20.507641	ACCEPTED	2025-12-24 16:47:42.266398	2026-01-23 15:47:00
2	7	4	2025-12-24 21:59:03.245011	ACCEPTED	2025-12-24 22:06:37.926718	2026-01-31 20:58:00
2	2	4	2025-12-24 22:32:52.95883	ACCEPTED	2025-12-24 22:46:39.404132	2026-01-31 21:32:00
\.


--
-- Data for Name: manuscripts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.manuscripts (id, title, abstract, keywords, author_id, theme_id, section_id, language_id, status, pdf_filename, last_revision_at, decision_at, published_at, created_at, updated_at) FROM stdin;
1	L’Intelligence Artificielle : concepts fondamentaux, applications et enjeux contemporains	Ce manuscrit présente une introduction claire à l’intelligence artificielle, en expliquant ses principes de base, ses principales technologies et ses domaines d’application. Il analyse l’impact de l’IA dans différents secteurs tels que la santé, l’éducation et l’économie, tout en abordant les enjeux éthiques, sociaux et technologiques liés à son développement et à son utilisation croissante.	intelligence artificielle, machine learning, deep learning, automatisation, technologies numériques, éthique	3	1	2	1	SUBMITTED	manuscripts/86c9f26a29a04dfc891fc8691e53af34.pdf	\N	\N	\N	2025-12-24 16:31:34.706138+00	2025-12-24 16:31:34.706166+00
2	Article AI	resume article ai	ai,ia	6	1	1	2	RE_SUBMITTED	manuscripts/463f325ddd1b4af196cd006155af1357.pdf	2025-12-24 22:40:59.379999	\N	\N	2025-12-24 21:47:03.810919+00	2025-12-24 22:40:59.371802+00
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, created_at, updated_at) FROM stdin;
1	SUPER_ADMIN	Super administrateur avec tous les droits	2025-12-24 16:15:40.917375	2025-12-24 16:15:40.917375
2	ADMIN	Administrateur du système	2025-12-24 16:15:40.917375	2025-12-24 16:15:40.917375
3	EDITOR	Éditeur de la plateforme	2025-12-24 16:15:40.917375	2025-12-24 16:15:40.917375
5	AUTHOR	Auteur de manuscrits	2025-12-24 16:15:40.917375	2025-12-24 16:15:40.917375
4	EVALUATOR	Évaluateur de manuscrits	2025-12-24 16:15:40.917375	2025-12-24 16:35:20.605484
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sections (id, name, signe_min, signe_max, created_at, updated_at) FROM stdin;
1	Analyses critiques	40000	50000	2025-12-24 16:23:14.174476	2025-12-24 16:23:14.174481
2	RegArts	25000	30000	2025-12-24 16:24:04.212086	2025-12-24 16:24:04.212089
3	Fiche interdisciplinaire	15000	15001	2025-12-24 16:25:13.583084	2025-12-24 16:25:13.583086
4	Recensions d’ouvrages	10000	10001	2025-12-24 16:25:38.432097	2025-12-24 16:25:38.432098
\.


--
-- Data for Name: themes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.themes (id, title, description, created_at, updated_at) FROM stdin;
1	Intelligence Artificielle	Ce thème explore les principes fondamentaux de l’intelligence artificielle, ses principales technologies et ses applications dans la vie quotidienne et professionnelle. \nIl met en lumière le rôle de l’IA dans l’automatisation, l’analyse des données et l’aide à la décision, tout en abordant les enjeux éthiques et sociétaux liés à son développement.	2025-12-24 16:28:15.616314	2025-12-24 16:28:15.616318
2	COMPUTE SCIENCE	CCCC	2025-12-24 21:41:10.295092	2025-12-24 21:41:10.295095
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (id, user_id, role_id, assigned_by, assigned_at) FROM stdin;
1	1	1	1	2025-12-24 16:15:40.917375
2	2	4	1	2025-12-24 16:19:19.15451
3	3	5	1	2025-12-24 16:19:58.835162
4	4	3	1	2025-12-24 16:20:36.046385
6	5	4	1	2025-12-24 16:37:53.489871
7	6	5	\N	2025-12-24 21:45:02.004099
9	7	4	1	2025-12-24 21:56:01.308578
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, email_verified, password_hash, full_name, profile_photo, orcid_id, is_active, bio, "position", institution, created_at, updated_at) FROM stdin;
1	santaane@gmail.com	t	$2b$12$o9YHq.8X5puP8bNcvofoOO.OXzhU3WjtHCo1dfuqsH0Dwxzvj6j6.	Super Admin Santaane	\N	\N	t	Administrateur principal de la plateforme Santaane	Super Administrateur	Santaane Platform	2025-12-24 16:15:40.917375+00	2025-12-24 16:15:40.917375+00
3	author@gmail.com	f	$2b$12$vdT3n4SoQJO/25Bq4iHsre51swYMQApdXgxz5XXBCQtDWYMwj33AO	Mouhamed Diop	\N	\N	t	\N	\N	\N	2025-12-24 16:19:58.780066+00	2025-12-24 16:21:03.05784+00
4	editor@gmail.com	f	$2b$12$Hn4NybglKR8jDqH1XrZzbeMCSsxIK2AS/r6CjJVor2n5YD8nj2YIe	Saliou Sarr	\N	\N	t	\N	\N	\N	2025-12-24 16:20:35.997543+00	2025-12-24 16:33:34.076018+00
5	e@gmail.com	f	$2b$12$mz3i9Uqwfcp5p/hXkmUzcuv8S7MushLQ3DImwCVo5/Svf47..lTXy	Hama Hama	\N		f				2025-12-24 16:36:18.886558+00	2025-12-24 21:37:08.770489+00
6	saliouauthor@gmail.com	f	$2b$12$kB34Tgka/Vg6VQEkIIefkOuJNUZzi4SaFDFsIDzNFHa6N8A/pxtmG	Saliou	\N	\N	t	\N	\N	\N	2025-12-24 21:45:01.98734+00	2025-12-24 21:45:01.987374+00
7	masamba@udju.com	f	$2b$12$HZbqYF2/zM6uHkl18IPxdukWF5qJZP0oDYXM1YUWa.sY0uBmAp8je	Massamba Massamba	\N		t				2025-12-24 21:53:49.233416+00	2025-12-24 21:58:21.188759+00
2	eval@gmail.com	f	$2b$12$qPaU1OEllh4PkiwBmAFzOuyvLA.ov0vf/Y7ehh8HB1hmA50VIQcEy	Hamadou	\N		t				2025-12-24 16:19:18.819055+00	2025-12-24 23:11:47.95286+00
\.


--
-- Name: cities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cities_id_seq', 1, false);


--
-- Name: countries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.countries_id_seq', 1, false);


--
-- Name: languages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.languages_id_seq', 2, true);


--
-- Name: manuscript_evaluation_grids_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.manuscript_evaluation_grids_id_seq', 1, false);


--
-- Name: manuscripts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.manuscripts_id_seq', 2, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sections_id_seq', 4, true);


--
-- Name: themes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.themes_id_seq', 2, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 9, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (id);


--
-- Name: countries countries_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_code_key UNIQUE (code);


--
-- Name: countries countries_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_name_key UNIQUE (name);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (id);


--
-- Name: manuscript_annotations manuscript_annotations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_annotations
    ADD CONSTRAINT manuscript_annotations_pkey PRIMARY KEY (id);


--
-- Name: manuscript_evaluation_grids manuscript_evaluation_grids_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluation_grids
    ADD CONSTRAINT manuscript_evaluation_grids_pkey PRIMARY KEY (id);


--
-- Name: manuscript_evaluators manuscript_evaluators_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluators
    ADD CONSTRAINT manuscript_evaluators_pkey PRIMARY KEY (manuscript_id, evaluator_id);


--
-- Name: manuscripts manuscripts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts
    ADD CONSTRAINT manuscripts_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: themes themes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.themes
    ADD CONSTRAINT themes_pkey PRIMARY KEY (id);


--
-- Name: manuscript_evaluation_grids uq_manuscript_evaluator; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluation_grids
    ADD CONSTRAINT uq_manuscript_evaluator UNIQUE (manuscript_id, evaluator_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_evaluation_grids_evaluator; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evaluation_grids_evaluator ON public.manuscript_evaluation_grids USING btree (evaluator_id);


--
-- Name: idx_evaluation_grids_manuscript; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_evaluation_grids_manuscript ON public.manuscript_evaluation_grids USING btree (manuscript_id);


--
-- Name: idx_manuscript_annotations_evaluator; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_manuscript_annotations_evaluator ON public.manuscript_annotations USING btree (evaluator_id);


--
-- Name: idx_manuscript_annotations_manuscript; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_manuscript_annotations_manuscript ON public.manuscript_annotations USING btree (manuscript_id);


--
-- Name: ix_languages_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_languages_code ON public.languages USING btree (code);


--
-- Name: ix_languages_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_languages_name ON public.languages USING btree (name);


--
-- Name: ix_manuscript_evaluators_assigned_by_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscript_evaluators_assigned_by_id ON public.manuscript_evaluators USING btree (assigned_by_id);


--
-- Name: ix_manuscripts_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_author_id ON public.manuscripts USING btree (author_id);


--
-- Name: ix_manuscripts_language_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_language_id ON public.manuscripts USING btree (language_id);


--
-- Name: ix_manuscripts_section_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_section_id ON public.manuscripts USING btree (section_id);


--
-- Name: ix_manuscripts_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_status ON public.manuscripts USING btree (status);


--
-- Name: ix_manuscripts_theme_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_theme_id ON public.manuscripts USING btree (theme_id);


--
-- Name: ix_manuscripts_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_manuscripts_title ON public.manuscripts USING btree (title);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_sections_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sections_name ON public.sections USING btree (name);


--
-- Name: ix_themes_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_themes_title ON public.themes USING btree (title);


--
-- Name: ix_user_roles_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_role_id ON public.user_roles USING btree (role_id);


--
-- Name: ix_user_roles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_roles_user_id ON public.user_roles USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: manuscript_evaluation_grids update_evaluation_grids_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_evaluation_grids_updated_at BEFORE UPDATE ON public.manuscript_evaluation_grids FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: manuscript_annotations update_manuscript_annotations_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_manuscript_annotations_updated_at BEFORE UPDATE ON public.manuscript_annotations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: cities cities_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: manuscript_annotations manuscript_annotations_evaluator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_annotations
    ADD CONSTRAINT manuscript_annotations_evaluator_id_fkey FOREIGN KEY (evaluator_id) REFERENCES public.users(id);


--
-- Name: manuscript_annotations manuscript_annotations_manuscript_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_annotations
    ADD CONSTRAINT manuscript_annotations_manuscript_id_fkey FOREIGN KEY (manuscript_id) REFERENCES public.manuscripts(id);


--
-- Name: manuscript_evaluation_grids manuscript_evaluation_grids_evaluator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluation_grids
    ADD CONSTRAINT manuscript_evaluation_grids_evaluator_id_fkey FOREIGN KEY (evaluator_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: manuscript_evaluation_grids manuscript_evaluation_grids_manuscript_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluation_grids
    ADD CONSTRAINT manuscript_evaluation_grids_manuscript_id_fkey FOREIGN KEY (manuscript_id) REFERENCES public.manuscripts(id) ON DELETE CASCADE;


--
-- Name: manuscript_evaluators manuscript_evaluators_assigned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluators
    ADD CONSTRAINT manuscript_evaluators_assigned_by_id_fkey FOREIGN KEY (assigned_by_id) REFERENCES public.users(id);


--
-- Name: manuscript_evaluators manuscript_evaluators_evaluator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluators
    ADD CONSTRAINT manuscript_evaluators_evaluator_id_fkey FOREIGN KEY (evaluator_id) REFERENCES public.users(id);


--
-- Name: manuscript_evaluators manuscript_evaluators_manuscript_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscript_evaluators
    ADD CONSTRAINT manuscript_evaluators_manuscript_id_fkey FOREIGN KEY (manuscript_id) REFERENCES public.manuscripts(id);


--
-- Name: manuscripts manuscripts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts
    ADD CONSTRAINT manuscripts_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: manuscripts manuscripts_language_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts
    ADD CONSTRAINT manuscripts_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(id);


--
-- Name: manuscripts manuscripts_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts
    ADD CONSTRAINT manuscripts_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: manuscripts manuscripts_theme_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manuscripts
    ADD CONSTRAINT manuscripts_theme_id_fkey FOREIGN KEY (theme_id) REFERENCES public.themes(id);


--
-- Name: user_roles user_roles_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict DXb3MLM6N9bpYGQ91NSpjcCqwSlihZqaYTYbVEPHguSmhHdEFwPPe7SGX9jnFFg

