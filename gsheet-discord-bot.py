import discord
import gspread
import textwrap
from pathlib import Path

gc = gspread.service_account()

# Sheet Token is found in URL of the sheet


p = Path(__file__).with_name('bot_token')
with p.open('r') as f:
    bot_token = f.readline()
    f.close()

p = Path(__file__).with_name('sheet_token')
with p.open('r') as f:
    sheet_token = f.readline()
    f.close()

sheet = gc.open_by_key(sheet_token)
trait_worksheet = sheet.get_worksheet(0)
character_worksheet = sheet.get_worksheet(2)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        if message.content.startswith('!'):
            data = message.content[1:].title()
            position = find_data(data, trait_worksheet, character_worksheet)
            if position[1] == "trait":
                # check for trait type
                trait_type = trait_worksheet.acell('B' + str(position[0])).value
                if trait_type == "Knowledge":
                    embed_var = format_trait_knowledge(trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                if trait_type == "Social":
                    embed_var = format_trait_social(trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)

            if position[1] == "character":
                image = format_name(character_worksheet, position[0])
                await message.channel.send(image)
            # asdf is for testing
            if position[1] == "asdf":
                embed_var = discord.Embed(title="adf", description="adsf", color=0x4000FF)
                embed_var.add_field(name="Test skill",value="-Some text",inline=False)
                embed_var2 = discord.Embed()
                embed_var2.add_field(name="Test skill",value="``` -Some more text```",inline=False)
                await message.channel.send(embed=embed_var)
                await message.channel.send(embed=embed_var2)

def format_effect_bullet(effect_line):
    combined_effect_line = ''
    initial_indent = ''
    sub_indent = initial_indent + ' '
    while (effect_line[1] == '-'):
        effect_line = effect_line[1:]
        initial_indent = sub_indent + ' '
        sub_indent = initial_indent + ' '
    effect_line = textwrap.wrap(text=effect_line, width=55, initial_indent=initial_indent, subsequent_indent=sub_indent)
    for i in range(len(effect_line)):
        combined_effect_line = combined_effect_line + effect_line[i] + '\n'
    return combined_effect_line

def create_embed_social(skill_name, field_names, descriptions):
    embed = discord.Embed()
    embed.title = skill_name
    embed.description = descriptions[0]
    embed.add_field(name=field_names[0], value=descriptions[1])
    embed.add_field(name=field_names[1], value=descriptions[2])
    embed.add_field(name=field_names[2], value=descriptions[3])
    embed.add_field(name=field_names[3], value=descriptions[4])
    embed.add_field(name=field_names[4], value=descriptions[5])
    embed.add_field(name=field_names[5], value=descriptions[6], inline=False)
    embed.add_field(name=field_names[6], value=descriptions[7])
    embed.add_field(name=field_names[7], value=descriptions[8])

    if len(descriptions[9].splitlines()) > 10:
        effects = descriptions[9].splitlines(True)
        effect_split = ["",""]
        for i in range(0,10):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[0] = effect_split[0] + effects[i]
        for i in range(10,len(descriptions[9].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[1] = effect_split[1] + effects[i]
        embed.add_field(name=field_names[8], value='```' + effect_split[0] + '```', inline=False)
        embed.add_field(name=field_names[8]+" (cont.)", value='```' + effect_split[1] + '```', inline=False)
    else:
        effects = descriptions[9].splitlines(True)
        effect_split = ''
        for i in range(len(descriptions[9].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split = effect_split + effects[i]
        embed.add_field(name=field_names[8], value='```' + effect_split + '```', inline=False)

    return embed

def create_embed_knowledge(skill_name, field_names, descriptions):
    embed = discord.Embed()
    embed.title = skill_name
    embed.description = descriptions[0]
    embed.add_field(name=field_names[0], value=descriptions[1])
    embed.add_field(name=field_names[1], value=descriptions[2])
    embed.add_field(name=field_names[3], value=descriptions[4])
    embed.add_field(name=field_names[2], value=descriptions[3], inline=False)
    if len(descriptions[5].splitlines()) > 10:
        effects = descriptions[5].splitlines(True)
        effect_split = ["",""]
        for i in range(0,10):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[0] = effect_split[0] + effects[i]
        for i in range(10,len(descriptions[5].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[1] = effect_split[1] + effects[i]
        embed.add_field(name=field_names[4], value='```' + effect_split[0] + '```', inline=False)
        embed.add_field(name=field_names[4]+" (cont.)", value='```' + effect_split[1] + '```', inline=False)
    else:
        effects = descriptions[5].splitlines(True)
        effect_split = ''
        for i in range(len(descriptions[5].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split = effect_split + effects[i]
        embed.add_field(name=field_names[4], value='```' + effect_split + '```', inline=False)

    # Used to get the length of entire discord embed
    # # embed would be the discord.Embed instance
    # fields = [embed.title, embed.description, embed.footer.text, embed.author.name]
    #
    # fields.extend([field.name for field in embed.fields])
    # fields.extend([field.value for field in embed.fields])
    #
    # total = ""
    # for item in fields:
    #     # If we str(discord.Embed.Empty) we get 'Embed.Empty', when
    #     # we just want an empty string...
    #     total += str(item) if str(item) != 'Embed.Empty' else ''

    # print(len(total))

    return embed

def format_trait_social(worksheet, skill_name, position):
    desc = ["","","","","","","","","",""]
    field_names = ["","","","","","","","",""]
    position = str(position)
    field_names[0] = level_cost = "Level Cost:"
    field_names[1] = level_limit = "Level Limit:"
    field_names[2] = disallowed = "Disallowed:"
    field_names[3] = type = "Type:"
    field_names[4] = timing = "Timing:"
    field_names[5] = requirements = "Requirements:"
    field_names[6] = players = "Player Character(s):"
    field_names[7] = slots = "Player Slot(s):"
    field_names[8] = effects = "Effects:"

    # Description
    val = worksheet.acell('L' + position).value
    desc[0] = val

    # Level Cost
    val = worksheet.acell('C' + position).value
    desc[1] = val

    # Level Limit
    val = worksheet.acell('D' + position).value
    desc[2] = val

    # Disallowed
    val = worksheet.acell('E' + position).value
    desc[3] = val

    # Type
    val = worksheet.acell('J' + position).value
    desc[4] = val

    # Timing
    val = worksheet.acell('I' + position).value
    desc[5] = val

    # Requirements
    val = worksheet.acell('F' + position).value
    desc[6] = val

    # Players
    val = worksheet.acell('G' + position).value
    desc[7] = val

    # Slots
    val = worksheet.acell('H' + position).value
    desc[8] = val

    # Effects
    val = worksheet.acell('K' + position).value
    desc[9] = val

    return create_embed_social(skill_name, field_names, desc)

def format_trait_knowledge(worksheet, skill_name, position):
    desc = ["","","","","",""]
    field_names = ["","","","",""]
    position = str(position)
    field_names[0] = level_cost = "Level Cost:"
    field_names[1] = level_limit = "Level Limit:"
    field_names[2] = requirements = "Requirements:"
    field_names[3] = type = "Type:"
    field_names[4] = effects = "Effects:"

    # Description
    val = worksheet.acell('H' + position).value
    desc[0] = val

    # Level Cost
    val = worksheet.acell('C' + position).value
    desc[1] = val

    # Level Limit
    val = worksheet.acell('D' + position).value
    desc[2] = val

    # Requirements
    val = worksheet.acell('E' + position).value
    desc[3] = val

    # Type
    val = worksheet.acell('F' + position).value
    desc[4] = val

    # Effects
    val = worksheet.acell('G' + position).value
    desc[5] = val

    x = len(desc[5].splitlines())
    print(x)

    return create_embed_knowledge(skill_name, field_names, desc)

def format_name(worksheet, position):
    position = str(position)
    message = worksheet.acell(format_position("B",position)).value
    return message

def check_message_length(message):
    print(len(message))
    return message

def format_position(letter, index):
    cell = letter + index
    return cell

def find_data(message, trait_worksheet, character_worksheet):
    list_of_traits = trait_worksheet.col_values(1)
    for i in range(len(list_of_traits)):
        # print("Hello: " + str(i) + list_of_traits[i])
        if list_of_traits[i] == message:
            return i+1,"trait"

    list_of_names = character_worksheet.col_values(1)
    for i in range(len(list_of_names)):
        # print("Hello: " + str(i) + list_of_names[i])
        if list_of_names[i] == message:
            return i+1,"character"

    return 0, "asdf"

client = MyClient()
client.run(bot_token)