import discord
import gspread
import textwrap

gc = gspread.service_account()
sheet = gc.open_by_key('SHEET TOKEN')
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
                message_array = format_trait(trait_worksheet, data, position[0])
                await message.channel.send(message_array[0])
                await message.channel.send(message_array[1])

            if position[1] == "character":
                image = format_name(character_worksheet, position[0])
                await message.channel.send(image)
            if position[1] == "asdf":
                embed_var = create_embed()
                await message.channel.send(embed=embed_var)

def create_embed():
    embed = discord.Embed()
    embed.title = "Title"
    embed.description = "Description"
    return embed

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
        print("Hello: " + str(i) + list_of_traits[i])
        if list_of_traits[i] == message:
            return i+1,"trait"

    list_of_names = character_worksheet.col_values(1)
    for i in range(len(list_of_names)):
        print("Hello: " + str(i) + list_of_names[i])
        if list_of_names[i] == message:
            return i+1,"character"

    return 0, "asdf"

client = MyClient()
client.run("BOT TOKEN")