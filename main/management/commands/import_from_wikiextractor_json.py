from django.core.management.base import BaseCommand, CommandError
from main.models import Article

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('weout', nargs='+', type=str)

    def handle(self, *args, **options):
        output=[]
        for folder in os.listdir(options["weout"]):
            for file in os.listdir(f"{options['weout']}/{folder}"):
                a=open(f"{options['weout']}/{folder}/{file}").read()
                for record in a.split("\n"):
                    if record:
                        output+=[[record["title"], record["text"]]]
                        print(output)

        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))