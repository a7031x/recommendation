import recommendations
import dataset
###################################################################
# Variables                                                       #
# When launching project or scripts from Visual Studio,           #
# input_dir and output_dir are passed as arguments automatically. #
# Users could set them from the project setting page.             #
###################################################################

def main():
    prefs = dataset.load_movie_lens()
#    r = recommendations.get_recommendations(prefs, '87')
#    print(r[0:30])
    itemsim = recommendations.sim_items(prefs, 50)
    r = recommendations.get_recommended_items(prefs, itemsim, '87')
    print(r[0:30])


main()
