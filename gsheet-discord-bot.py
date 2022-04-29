import discord
import gspread
import textwrap
from pathlib import Path

gc = gspread.service_account()

# Bot token refers to the Discord bot token
p = Path(__file__).with_name('bot_token')
with p.open('r') as f:
    bot_token = f.readline()
    f.close()

# Sheet Token is found in URL of the sheet
p = Path(__file__).with_name('sheet_token')
with p.open('r') as f:
    sheet_token = f.readline()
    f.close()

# This opens the Google Sheet and then accesses the relevant sheets that need to be parsed
sheet = gc.open_by_key(sheet_token)
trait_worksheet = sheet.get_worksheet(0)
character_worksheet = sheet.get_worksheet(1)
gear_worksheet = sheet.get_worksheet(2)

# These descriptors are used for the field names in the Discord Embed
knowledge_descriptors = ["Level Cost", "Level Limit", "Requirements", "Type", "Effects"]
skill_descriptors = ["Level Cost", "Level Limit", "Requirements", "Type", "Effects"]
social_descriptors = ["Level Cost", "Level Limit", "Disallowed", "Requirements", "Player Characters", "Player Slots", "Timing", "Type", "Effects"]
third_eye_descriptors = ["Level Cost", "Level Limit", "Disallowed", "Requirements", "Player Characters", "Player Slots", "Type", "Effects"]
sink_descriptors = ["Level Cost", "Requirements", "Type", "Effects"]
equip_descriptors = ["Disallowed", "Equipment" "Slot", "Eye Compatibility", "Level" "Cost", "Level Limit", "MP", "Penalty", "Placement", "Requirements", "Type", "Effects"]
adv_equip_descriptors = ["Disallowed", "Equipment" "Slot", "Eye Compatibility", "Level" "Cost", "Level Limit", "MP", "Player Characters", "Player Slots", "Penalty", "Placement", "Producer", "Requirements", "Type", "Effects"]

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        if message.content.startswith('!'):

            data = message.content[1:].title()
            position = find_data(data, trait_worksheet, character_worksheet, gear_worksheet)
            if position[1] == "trait":
                # check for trait type
                trait_type = trait_worksheet.acell('B' + str(position[0])).value

                if trait_type == "Knowledge" or trait_type == "Skill":
                    embed_var = format_trait_general(knowledge_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                elif trait_type == "Social":
                    embed_var = format_trait_general(social_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                elif trait_type == "Third Eye":
                    embed_var = format_trait_general(third_eye_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                elif trait_type == "Sink":
                    embed_var = format_trait_general(sink_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                elif trait_type == "Equipment":
                    embed_var = format_trait_general(equip_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)
                elif trait_type == "Advanced Equipment":
                    embed_var = format_trait_general(adv_equip_descriptors, trait_worksheet, data, position[0])
                    await message.channel.send(embed=embed_var)

            if position[1] == "character":
                image = format_name(character_worksheet, position[0])
                await message.channel.send(image)

            if position[1] == "gear":
                image = format_name(gear_worksheet, position[0])
                await message.channel.send(image)

            # asdf is for testing
            if position[1] == "asdf":
                embed_var = discord.Embed(title="adf", description="adsf", color=0x4000FF)
                embed_var.add_field(name="Test skill",value="-Some text",inline=False)
                embed_var2 = discord.Embed()
                embed_var2.add_field(name="Test skill",value="``` -Some more text```",inline=False)
                await message.channel.send(embed=embed_var)
                await message.channel.send(embed=embed_var2)

def format_trait_general(field_names, worksheet, skill_name, position):
    desc = [None] * (len(field_names) + 1)
    position = str(position)

    print("length of desc: " + str(len(desc)))

    # This will take the data of a cell, then increment the LETTER (column) to take in the next field data.
    # this means that data is to be filled via columns, left to right.
    # In this case, my data begins in column C (A is the name, B is an identifier)
    for i in range(len(desc)):
        starting_letter = 'C'
        cell = chr(ord(starting_letter) + i)
        val = worksheet.acell(cell + position).value
        desc[i] = val

    return create_embed_general(skill_name, field_names, desc)

# Field creation. It is dynamic based on the field descriptors at the top of the script
def create_embed_general(skill_name, field_names, descriptions):
    effect_position = len(descriptions)-1
    embed = discord.Embed()
    embed.title = skill_name
    embed.description = descriptions[0]
    
    for i in range(len(field_names)-1):
        if field_names[i] == "Requirements":
            embed.add_field(name=field_names[i], value=descriptions[i + 1], inline=False)
        else:
            embed.add_field(name=field_names[i], value=descriptions[i+1])

    # Important to understand that Discord Embed fields have a limit of 1024 characters
    # The logic below does NOT currently dynamically deal with descriptors larger than 1024 characters
    # Currently it splices a string if there are more than 10 lines and then hopefully the fields are below the limit
    # Possible: check for 1024 characters, splice at the line before detection, and continue?
    if len(descriptions[effect_position].splitlines()) > 10:
        effects = descriptions[effect_position].splitlines(True)
        effect_split = ["",""]
        for i in range(0,7):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[0] = effect_split[0] + effects[i]
        for i in range(7,len(descriptions[effect_position].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split[1] = effect_split[1] + effects[i]
        embed.add_field(name=field_names[effect_position-1], value='```' + effect_split[0] + '```', inline=False)
        embed.add_field(name=field_names[effect_position-1]+" (cont.)", value='```' + effect_split[1] + '```', inline=False)
    else:
        effects = descriptions[effect_position].splitlines(True)
        effect_split = ''
        for i in range(len(descriptions[effect_position].splitlines())):
            effects[i] = format_effect_bullet(effects[i])
            effect_split = effect_split + effects[i]
        embed.add_field(name=field_names[effect_position-1], value='```' + effect_split + '```', inline=False)

    return embed

# Taking data from Google Sheets will sometimes wipe leading white space,
# which means it is difficult to created bulleted Embeds.
# This function assumes the user is formating the Google Sheet in the following way:
# 1. Bullet points are denoted with -
# 2. Indents are denoted with additional -, so a an indented bullet looks like --
# This function will parse that logic and return with a usable string
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

# Used to return the value of a cell in the 2nd column of a Google Sheet. Narrow usage.
def format_name(worksheet, position):
    position = str(position)
    message = worksheet.acell(format_position("B",position)).value
    return message

# Used to aid in finding the value of a cell by taking in a letter(column) and number(row).
# Has potential to help clean code, but currently narrow usage.
def format_position(letter, index):
    cell = letter + index
    return cell

def check_message_length(message):
    print(len(message))
    return message

# This scraps every sheet for the input given.
# If it is found, then the function halts and returns the result
def find_data(message, trait_worksheet, character_worksheet, gear_worksheet):
    list_of_traits = trait_worksheet.col_values(1)
    message = message.lower()
    for i in range(len(list_of_traits)):
        # print("Hello: " + str(i) + list_of_traits[i])
        if list_of_traits[i].lower() == message:
            return i+1,"trait"

    list_of_names = character_worksheet.col_values(1)
    for i in range(len(list_of_names)):
        # print("Hello: " + str(i) + list_of_names[i])
        if list_of_names[i].lower() == message:
            return i+1,"character"

    list_of_names = gear_worksheet.col_values(1)
    for i in range(len(list_of_names)):
        # print("Hello: " + str(i) + list_of_names[i])
        if list_of_names[i].lower() == message:
            return i+1,"gear"

    return 0, "asdf"

client = MyClient()
client.run(bot_token)