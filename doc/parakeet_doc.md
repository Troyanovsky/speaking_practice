There are different parakeet libraries for ASR on windows with Nvidia GPU vs MacOS.

## Mac OS
Use the parakeet-mlx library
```
uv add parakeet-mlx -U

from parakeet_mlx import from_pretrained

model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v3")

result = model.transcribe("audio_file.wav")

print(result.text)
```

## Windows
Use the nemo_toolkit. We recommend you install it after you've installed latest PyTorch version.

The model is available for use in the NeMo toolkit, and can be used as a pre-trained checkpoint for inference or for fine-tuning on another dataset.

```
pip install -U nemo_toolkit['asr']

# Automatically instantiate the model
import nemo.collections.asr as nemo_asr
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3")

# Transcribing using Python
output = asr_model.transcribe(['input.wav'])
print(output[0].text)
```
