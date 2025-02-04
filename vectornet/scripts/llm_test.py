import openai
import os
from traceback import print_exception
import openai
import os
from dotenv import load_dotenv

load_dotenv()
api_key=os.environ["OPENAI_API_KEY"]

llm_client = openai.OpenAI(
    api_key = api_key,
    max_retries=3,
)

def generate_query_content(llm_client, content):
    prompt = (
        """You are an embedding evaluator. Your task is to generate a query from the given original content to assess how well the embedding engines perform.
        You will be provided with the original content as your source of information. Your job is to create a summarized version of this content.
        This summary will be used to evaluate the performance quality of different embedding engines by comparing the embeddings of the query content with the results from each engine."""
    )
    prompt += content + " "
    prompt += (
        """Generate a summary of the original content using approximately 700-900 characters. Provide only the generated summary in plain text, without any additional context, explanation, or formatting. single and double quotes or new lines."""
    )

    try:
        output = llm_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=1.5,
            timeout=30,
        )

        print(
            f"generation questions LLM response: {output.choices[0].message.content}"
        )
        print(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        return output.choices[0].message.content
    except Exception as e:
        print(f"Error during LLM completion: {e}")
        print(print_exception(type(e), e, e.__traceback__))
        
        
content = 'Paines Plough is a touring theatre company founded in 1974, currently led by Artistic Directors Charlotte Bennett and Katie Posner. The company exclusively commissions and produces new plays and helps playwrights develop their craft. Over the past four decades, Paines Plough has established itself as a leading new writing company producing work by a wide range of playwrights across the UK and abroad. Collaboration with other theatre organisations is a vital feature of the company’s work and since 2010 the company has co-produced every show theyve worked on with either a venue or a touring partner. In 2005, Paines Plough launched Future Perfect in conjunction with Channel 4. The scheme is a year-long attachment for emerging playwrights. Writers who have taken part include Lizzie Nunnery, Tom Morton-Smith and Duncan Macmillan. In October 2010, the company won a TMA award for special achievement in regional theatre. == History == Paines Plough was formed in 1974 over a pint of Paines bitter in the Plough pub by playwright David Pownall and director John Adams. For over 40 years the company has commissioned, produced and toured new plays all over Britain and internationally. In 2019 Artistic Directors Katie Posner and Charlotte Bennett were approached by Ellie Keel with the idea to create an award for female playwrights, to recognise these figures in the theatre world. The three launched the Womens Prize for Playwriting at the end of that year and have continued to support it ever since. == Artistic directors == == Roundabout == Roundabout is Paines Ploughs touring in-the-round auditorium. Roundabout was designed by Lucy Osborne and Emma Chapman in collaboration with Charcoalblue and Howard Eaton. It was built and developed by Factory Settings. In 2010, Roundabout was commissioned, with a prototype built in 2011 with Sheffield Theatres. The opening season of Roundabout consisted of three new plays performed in repertory One Day When We Were Young by Nick Payne, Lungs by Duncan Macmillan and The Sound of Heavy Rain by Penelope Skinner. In 2014, Roundabout was re-imagined to allow for touring. As part of Paines Ploughs 40th anniversary celebrations a new season was commissioned for Roundabout. The plays debuted at Edinburgh Festival Fringe at Summerhall: Our Teachers A Troll by Dennis Kelly, The Initiate by Alexandra Wood and Lungs and Every Brilliant Thing by Duncan Macmillan. After the run in Edinburgh Roundabout toured nationally to: Corn Exchange, Margate Theatre Royal, Hackney Showroom and The Civic in Barnsley. Roundabout won the Theatre Building of the Year award at The Stage Awards. In 2015, Roundabout toured with the same programme but added one new play to the repertory The Human Ear by Alexandra Wood. The auditorium once again took up residency at Summerhall for Edinburgh Festival Fringe before touring nationally to: Corn Exchange, Margate Theatre Royal, Southbank Centre, The Lowry, Lincoln Performing Arts Centre, Brewery Arts Centre in Kendal and Appetite in Stoke. At the end of 2015, Paines Plough were granted money as part of Arts Council Englands Strategic Touring Fund to tour Roundabout from 2016 to 2018 with seven nationwide partner venues: The Civic in Barnsley, Margate Theatre Royal, RevoLuton, Hall For Cornwall, The Lowry, Lincoln Performing Arts Centre, Brewery Arts Centre in Kendal and Appetite in Stoke. They will each receive a repertory of three new plays commissioned and produced by Paines Plough and partners. The Roundabout plays for 2016 are Love, Lies and Taxidermy by Alan Harris, Growth by Luke Norris and I Got Superpowers for My Birthday by Katie Douglas. == Productions == === 2016 === With a Little Bit of Luck by Sabrina Mahfouz, directed by Stef ODriscoll and co-produced with Latitude Festival Broken Biscuits by Tom Wells, directed by James Grieve and co-produced with Live Theatre Ten Weeks by Elinor Cook, directed by Kate Wasserberg and co-produced with Royal Welsh College of Music and Drama Growth by Luke Norris, directed by George Perrin Love, Lies and Taxidermy by Alan Harris, directed by George Perrin and co-produced by Sherman Cymru and Theatr Clwyd I Got Superpowers for My Birthday by Katie Douglas, directed by George Perrin and co-produced with Halfmoon Theatre Bilals Birthday by Nathan Bryon, directed by Liz Carlson and co-produced by Naked Angels 322 Days by Lucy Gillespie, directed by Sean Linnen and co-produced by Naked Angels Come To Where Im From === 2021 === Reasons You Should(nt) Love Me by Amy Trigg, directed by Charlotte Bennett and co-produced with The Women’s Prize for Playwriting, 45North, Kiln Theatre. === 2022 === Hungry by Chris Bush, directed by Katie Posner and co-produced with 45North and Belgrade Theatre Sorry Youre Not A Winner by Samuel Bailey, directed by Jesse Jones and co-produced with Theatre Royal Plymouth Black Love by Chinonyerem Odimba, directed by Chinonyerem Odimba and co-produced with Kiln Theatre and tiata fahodzi. The Ultimate Pickle by Laura Lindow, directed by Eva Sampson and co-produced with Rose Theatre Kingston for the Roundabout 2022 season. Half-Empty Glasses by Dipo Baruwa-Etti, directed by Kaleya Baxe and co-produced with Rose Theatre for the Roundabout 2022 season. A Sudden Violent Burst of Rain by Sami Ibrahim, directed by Yasmin Hafesji and co-produced with Rose Theatre for the Roundabout 2022 season. === 2023 === Strategic Love Play by Miriam Battye, directed by Katie Posner and co-produced with Soho Theatre, Belgrade Theatre and Landmark Theatres. Bullring Techno Makeout Jamz by Nathan Queeley-Dennis, directed by Dermot Daly and co-produced with Ellie Keel Productions, Belgrade Theatre in association with the Royal Exchange Theatre. This is not a Coup by Mufaro Makubika, directed by Titas Halder in partnership with Royal Welsh College of Music and Drama You Bury Me by Ahlam, directed by Katie Posner and co-produced with The Women’s Prize for Playwriting, 45North, Royal Lyceum Theatre and the Orange Tree Theatre, in association with Bristol Old Vic. == References == == External links == Official website'

query_content = generate_query_content(llm_client, content)
print(query_content)
