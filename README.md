# SincNet-Tensorflow
Tensorflow implementation of SincNet ([Ravanelli & Bengio](https://github.com/mravanelli/SincNet)) and its application to decode motor imagination from EEG data

## Results 

The model reaches a classification accuracy of 87%

![accuracy_sinc_32filt](https://user-images.githubusercontent.com/55695116/174432422-a276060d-aeb8-4008-97d7-9eb8883c9843.png)

## Interpretation

These are the band pass filters learned by the model during training. We can see that the brain rhythms that help most in discrimination between different imagined movemement are the alpha rhythm and low beta rhythm.

![32_filters_SincShallowNet](https://user-images.githubusercontent.com/55695116/174432418-de04c434-34f3-40e9-a2bb-c35e81a4bd47.png)
