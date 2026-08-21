from django.db import migrations, models
import filer.fields.image


ABOUT_BODY = """<p>Matt Stevenson is a musician and producer in Portland, OR, USA. His most recent work is being released under the moniker BTMFDR (bottom feeder).</p>

<p>Originally from North Carolina, Matt explored a variety of musical styles and compositional approaches while contributing to the NC music scene from 2006 to 2017. His most notable work was with heavy music band MAKE, of which Matt was a founder and original drummer. Matt's tenure as the group's drummer spanned nearly a decade, and included multiple releases and several tours.</p>

<p>In 2012, Matt began exploring a new interest in house, techno, and electronic music in general. Performing and producing under his own name, Matt became a regular fixture of NC’s electronic music scene, primarily performing live dance sets. In 2014 he released his first solo album, <em>Infrastructure</em>, a lo-fi house excursion on cassette via now defunct GFR.</p>

<p>Over time, Matt's live sets began to combine his penchant for dark, heavy music with his love of fog-choked dance floors. His approach resonated with local audiences, and saw Matt host and perform at numerous events, the most notable being a pair shows for Moogfest in 2015.</p>

<p>An avid collaborator, Matt performed and produced in conjunction with many other artists during this time, including Clarq Blomquist (Kingsbury Manx, Tegguchigalpan), thefacesblur, The Hem of His Garment, Andrew Marlin, Natural Causes, and others. Matt was also featured on the compilation <em>Radar Love</em> from Activ-Analog Records as one half of J Rez (the other half being frequent collaborator Pothos Traxx).</p>

<p>In the Summer of 2017, Matt left his home behind to explore the west coast of the USA, settling in Portland, Oregon amidst record heat and wildfire smoke. Matt's next EP, <em>Bordered Entities</em>, was released shortly after this move, and comprised mostly of tracks written in North Carolina. It would be another five years until Matt would release any new music; between job changes, Covid, school, and all the vagaries of life, Matt found little energy to focus on music. Still, he was not totally dormant, and he continued his practice of musical creation and collaboration.</p>

<p>In 2022, Matt released <em>Dogs Can't Dance</em>, a three-track EP with three flavors of dub techno; the first track in particular exemplifies the sound of Matt's past live dance sets, with plenty of deep bass and dubbed out percussion.</p>

<p>In August 2026, Matt released <em>Time Was</em> - his first release under his new alias BTMFDR. The EP’s five tracks span thirty minutes, and move from dark ambience to harsh, blown-out soundscapes. <em>Time Was</em> also serves as the first release of Matt’s tape imprint Shift Witness; a limited first-edition of ten tapes was released in October, 2026.</p>"""


def create_about_article(apps, schema_editor):
    Article = apps.get_model('pages', 'Article')
    Article.objects.get_or_create(
        title='About',
        defaults={
            'image_credit': 'Nicole Kurtz',
            'body': ABOUT_BODY,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0008_alter_release_legacy_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=300)),
                ('image_credit', models.CharField(blank=True, max_length=200)),
                ('body', models.TextField(help_text='Use the rich text editor to format the article body and add links or images.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='+', to='filer.image')),
            ],
            options={'ordering': ('title', '-pk')},
        ),
        migrations.RunPython(create_about_article, migrations.RunPython.noop),
    ]