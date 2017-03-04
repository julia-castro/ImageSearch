from django.shortcuts import render
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import os
from searchengine.settings import BASE_DIR
from .forms import Search

def index(request):
  app = ClarifaiApp()
  processed_images = app.inputs.check_status().processed
  lines = []

  with open(os.path.join(BASE_DIR, 'images.txt'), "r") as f:
    for line in f:
      lines.append(line.rstrip('\n'))
    f.close()

  num_of_images = len(lines)
  batch = []
  max_batch_length = 128
  mod = num_of_images%max_batch_length

  if processed_images < num_of_images:
    for x in lines:
      batch.append(ClImage(url=x))
      if mod and (lines.index(x) < mod):
        if len(batch) == mod:
          app.inputs.bulk_create_images(batch)
          batch = []
      if len(batch) == max_batch_length:
        app.inputs.bulk_create_images(batch)
        batch = []

  top_ten = []
  message = ''

  if request.method == 'POST':
    form = Search(request.POST)
    if form.is_valid():
      try:
        concept = form.cleaned_data['search_term'].lower()
        images = app.inputs.search_by_predicted_concepts(concept=concept)
        top_ten = sorted(images, key=lambda image: image.score, reverse=True)[:10]
      except:
        message = 'Sorry, no images match your search term %s if you are searching in the plural ie "cats," try the term in the singular ie "cat"' % (form.cleaned_data['search_term'].lower())
  else:
    form = Search()

  context = {
    'form': form
  }
  if top_ten:
    context['hits'] = []
    for x in top_ten:
      context['hits'].append({'url': x.url, 'score': x.score})

  if message:
    context['message'] = message

  return render(request, 'imagesearch/index.html', context)