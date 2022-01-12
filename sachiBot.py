import discord
import gspread
import textwrap
from pathlib import Path

gc = gspread.service_account()

# Sheet Token is found in URL of the sheet
bot_token = ""
sheet_token = ""
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
            data = message.content[1:]
            position = find_data(data, trait_worksheet, character_worksheet)
            if position[1] == "trait":
                embed_var = format_trait3(trait_worksheet, data, position[0])
                await message.channel.send(embed=embed_var)

            if position[1] == "character":
                image = format_name(character_worksheet, position[0])
                await message.channel.send(image)
            # asdf is for testing
            if position[1] == "asdf":
                embed_var = discord.Embed(title="adf", description="adsf")
                embed_var.add_field(name="Test skill",value="Some text",inline=False)
                embed_var2 = discord.Embed()
                embed_var2.add_field(name="Test skill",value="Some more text",inline=False)
                await message.channel.send(embed=embed_var)
                await message.channel.send(embed=embed_var2)

def create_embed(skill_name, description):
    embed = discord.Embed()
    embed.title = skill_name
    embed.description = description
    return embed

def create_embed2(skill_name, field_names, descriptions):
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
            effect_split[0] = effect_split[0] + effects[i]
        for i in range(10,len(descriptions[5].splitlines())):
            effect_split[1] = effect_split[1] + effects[i]
        embed.add_field(name=field_names[4], value=effect_split[0], inline=False)
        embed.add_field(name=field_names[4]+" (cont.)", value=effect_split[1], inline=False)
    else:
        embed.add_field(name=field_names[4], value=descriptions[5], inline=False)

    # embed would be the discord.Embed instance
    fields = [embed.title, embed.description, embed.footer.text, embed.author.name]

    fields.extend([field.name for field in embed.fields])
    fields.extend([field.value for field in embed.fields])

    total = ""
    for item in fields:
        # If we str(discord.Embed.Empty) we get 'Embed.Empty', when
        # we just want an empty string...
        total += str(item) if str(item) != 'Embed.Empty' else ''

    print(len(total))

    return embed

# try to code if effects reset after 9 lines
def create_embed3():
    return 0

# Try to code if effects reset after 9 lines
def format_trait4(worksheet, skill_name, position):
    return 0

def format_trait3(worksheet, skill_name, position):
    desc = ["","","","","",""]
    field_names = ["","","","",""]
    position = str(position)
    field_names[0] = level_cost = "Level Cost:"
    field_names[1] = level_limit = "Level Limit:"
    field_names[2] = requirements = "Requirements:"
    field_names[3] = type = "Type:"
    field_names[4] = effects = "Effects:"

    # Description
    val = worksheet.acell(format_position("G", position)).value
    desc[0] = val

    # Level Cost
    val = worksheet.acell(format_position("B", position)).value
    desc[1] = val

    # Level Limit
    val = worksheet.acell('C' + position).value
    desc[2] = val

    # Requirements
    val = worksheet.acell('D' + position).value
    desc[3] = val

    # Type
    val = worksheet.acell('E' + position).value
    desc[4] = val

    # Effects
    val = worksheet.acell('F' + position).value
    desc[5] = val

    x = len(desc[5].splitlines())
    print(x)

    return create_embed2(skill_name, field_names, desc)

def format_trait2(worksheet, skill_name, position):
    desc = ""
    position = str(position)
    level_cost = "Level Cost: "
    level_limit = "Level Limit: "
    requirements = "Requirements: "
    type = "Type: "
    effects = "Effects: \n"

    # Description
    val = worksheet.acell(format_position("G", position)).value
    desc = desc + val + '\n'

    # Level Cost
    val = worksheet.acell(format_position("B", position)).value
    desc = desc + level_cost + val + '\n'

    # Level Limit
    val = worksheet.acell('C' + position).value
    desc = desc + level_limit + val + '\n'

    # Requirements
    val = worksheet.acell('D' + position).value
    desc = desc + requirements + val + '\n'

    # Type
    val = worksheet.acell('E' + position).value
    desc = desc + type + val + '\n'

    # Effects
    val = worksheet.acell('F' + position).value
    desc = desc + effects + val + '\n'

    return create_embed(skill_name, desc)



def format_trait(worksheet, skill_name, position):
    position = str(position)
    level_cost = "Level Cost: "
    level_limit = "Level Limit: "
    Requirements = "Requirements: "
    Type = "Type: "
    Effects = "Effects: \n"

    message = ["",""]
    message[0] = '```' "\n"
    message[0] = message[0] + skill_name + "\n"
    val = worksheet.acell(format_position("G",position)).value
    message[0] = message[0] + val + '\n'
    val = worksheet.acell(format_position("B",position)).value
    message[0] = message[0] + '```'

    message[1] = '```' + "\n"
    message[1] = message[1] + level_cost + val + '\n'
    val = worksheet.acell('C' + position).value
    message[1] = message[1] + level_limit + val + '\n'
    val = worksheet.acell('D' + position).value
    message[1] = message[1] + Requirements + val + '\n'
    val = worksheet.acell('E' + position).value
    message[1] = message[1] + Type + val + '\n'
    val = worksheet.acell('F' + position).value
    message[1] = message[1] + Effects + val + '\n'
    message[1] = message[1] + '```'
    return message

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