from comet_ml import Experiment, APIExperiment, API
import random

random.seed(1012)

e = Experiment(project_name="histogram_bug")

EPOCHS = 3
STEPS = 3
SIZE = 1000
MAX_TRIES = 20

def make_values(mu, sigma):
    return [random.gauss(mu, sigma) for r in range(SIZE)]

print("Logging...")
for epoch in range(EPOCHS):
    for step in range(STEPS):
        e.log_histogram_3d(make_values(epoch * 10, 1 + step),
                           "%s/v1" % epoch,
                           step=step)

print("Uploading...")
e.end()

print("Testing...")
api = API(cache=False)
apie = APIExperiment(previous_experiment=e.id, api=api)

histograms_json = apie.get_asset_list("histogram_combined_3d")
count = 0
while len(histograms_json) != EPOCHS and count < MAX_TRIES:
    print("Retry get assets...")
    histograms_json = apie.get_asset_list("histogram_combined_3d")
    count += 1

if count == MAX_TRIES:
    print(
        "ERROR: missing histogram at %s :" %
        (apie.url + "?experiment-tab=histograms",)
    )

for histogram_json in histograms_json:
    asset_id = histogram_json["assetId"]
    histogram = apie.get_asset(asset_id, return_type="json")

    if (len(histogram["histograms"]) != STEPS):
        print(
            "ERROR: histogram %s missing step at %s :" %
            (asset_id, apie.url + "?experiment-tab=histograms")
        )