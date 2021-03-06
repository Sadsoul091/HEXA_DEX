import re
import os

import pokepy
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

from pokemon import pokemon_text
from moveset import moveset_text
from locations import locations_text
from markup import data_markup, moveset_markup, locations_markup

BOT_TOKEN = os.environ.get("BOT_TOKEN", "1888295894:AAFBIF1bFNDX1dWsZrIuYJa_pNU7NSgvq8o")
API_ID = int(os.environ.get("API_ID", 3243264))
API_HASH = os.environ.get("API_HASH", "dc8004a68ca90a38c074d2c816d4b1cf")
app = Client("Poke-Bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
pk = pokepy.V2Client()
user_dict = {}
with open("pkmn.txt") as f:
    pokemon_list = [pkmn[:-1] for pkmn in f.readlines()]


@app.on_inline_query()
def main(app, inline_query):
    if len(inline_query.query) < 3:
        inline_query.answer(
            results=[],
            switch_pm_text="Help",
            switch_pm_parameter="start",
            cache_time=5
        )
        return
    matches = [pkmn for pkmn in pokemon_list if inline_query.query.lower() in pkmn.lower()]
    results = []
    for pkmn in matches:
        pkmn_data = pk.get_pokemon(pkmn)
        species = pk.get_pokemon_species(pkmn)
        name = species.names[7].name
        thumb_url = pkmn_data.sprites.front_default.replace("pokemon", "pokemon/other/official-artwork")
        markup = data_markup(name, expanded=0)
        typing = " / ".join([ty.type.name.title() for ty in pkmn_data.types])
        genus = species.genera[7].genus
        results.append(
            InlineQueryResultArticle(
                title=name,
                description=f"{genus}\nType: {typing}",
                input_message_content=InputTextMessageContent(f"🔄 Loading..."),
                thumb_url=thumb_url,
                reply_markup=markup
            )
        )
    user_dict[inline_query.from_user.id] = {results[i].id: results[i].title for i in range(len(results))}
    inline_query.answer(results=results, cache_time=3)


@app.on_chosen_inline_result()
def chosen(app, inline_query):
    name = user_dict[inline_query.from_user.id][inline_query.result_id]
    text = pokemon_text(pk, name, expanded=0)
    markup = data_markup(name, expanded=0)
    app.edit_inline_text(
        inline_message_id=inline_query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "infos" in query.data))
def expand(app, query):
    expanded = int(re.split("/", query.data)[1])
    pkmn = re.split("/", query.data)[2]
    text = pokemon_text(pk, pkmn, expanded=expanded)
    markup = data_markup(pkmn, expanded=expanded)
    app.answer_callback_query(query.id)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "moveset" in query.data))
def moveset(app, query):
    page = int(re.split("/", query.data)[1])
    pkmn = re.split("/", query.data)[2]
    text = moveset_text(pk, pkmn, page)
    markup = moveset_markup(pk, pkmn, page)
    app.answer_callback_query(query.id)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_callback_query(filters.create(lambda _, __, query: "locations" in query.data))
def locations(app, query):
    pkmn = re.split("/", query.data)[1]
    text = locations_text(pk, pkmn)
    markup = locations_markup(pkmn)
    app.edit_inline_text(
        inline_message_id=query.inline_message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=markup
    )


@app.on_message(filters.command("start"))
def start(app, message):
    text = """⚡️ KON'NICHIWA.... 
    I am the official POKEDEX of the group POKEMON TRAINER CLUB.
    Accessing me is very easy just TAG me with my username @PTC_dex_ROBOT and then type any pokemon name. Congratulations! you got the pokemon info you are looking for.
    I was made by a person called https://t.me/The_Sad_XX_Soul, A life long SAD PERSON. """
    app.send_message(
        chat_id=message.from_user.id,
        text=text
    )


app.run()
