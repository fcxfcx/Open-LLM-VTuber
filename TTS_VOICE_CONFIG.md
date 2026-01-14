# TTS 音色配置指南

本文档介绍如何在 Open-LLM-VTuber 项目中配置不同 TTS 引擎的音色。

## 配置位置

所有 TTS 配置都在 `conf.yaml` 文件的 `tts_config` 部分。根据您使用的 TTS 引擎，修改对应的配置项。

## 各 TTS 引擎音色配置

### 1. Azure TTS

**配置项：** `voice`

```yaml
azure_tts:
  api_key: 'your-azure-api-key'
  region: 'eastus'
  voice: 'en-US-AshleyNeural'  # 修改这里来更换音色
  pitch: '26'
  rate: '1'
```

**可用音色示例：**
- 中文：`zh-CN-XiaoxiaoNeural`（晓晓，女声）
- 中文：`zh-CN-YunxiNeural`（云希，男声）
- 英文：`en-US-AriaNeural`（女声）
- 英文：`en-US-GuyNeural`（男声）
- 日文：`ja-JP-NanamiNeural`（女声）

**查看所有可用音色：**
访问 [Azure TTS 语音列表](https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?tabs=tts)

### 2. Edge TTS

**配置项：** `voice`

```yaml
edge_tts:
  voice: 'zh-CN-XiaoxiaoNeural'  # 修改这里来更换音色
```

**查看所有可用音色：**
在命令行运行：
```bash
edge-tts --list-voices
```

**常用音色示例：**
- 中文：`zh-CN-XiaoxiaoNeural`（晓晓，女声）
- 中文：`zh-CN-YunxiNeural`（云希，男声）
- 英文：`en-US-AvaMultilingualNeural`（多语言女声）
- 日文：`ja-JP-NanamiNeural`（女声）

### 3. Piper TTS

**配置项：** `model_path` 和 `speaker_id`

```yaml
piper_tts:
  model_path: 'models/piper/zh_CN-huayan-medium.onnx'  # 模型路径，不同模型对应不同音色
  speaker_id: 0  # 对于多说话人模型，修改这里选择不同说话人
```

**更换音色方法：**
1. 下载不同的 Piper 模型（不同模型对应不同音色）
2. 修改 `model_path` 指向新模型
3. 如果是多说话人模型，调整 `speaker_id`

**模型下载：**
访问 [Piper 模型仓库](https://github.com/rhasspy/piper/releases)

### 4. CosyVoice / CosyVoice2

**配置项：** `sft_dropdown`（预训练音色）或 `prompt_wav_upload_url`（语音克隆）

```yaml
cosyvoice_tts:
  client_url: 'http://127.0.0.1:50000/'
  mode_checkbox_group: '预训练音色'  # 或 '3s极速复刻' 用于语音克隆
  sft_dropdown: '中文女'  # 预训练音色选项
  prompt_wav_upload_url: 'https://...'  # 语音克隆时使用的参考音频
```

**预训练音色选项：**
- `中文女`、`中文男`
- `英文女`、`英文男`
- `日文女`、`日文男`

### 5. Melo TTS

**配置项：** `speaker`

```yaml
melo_tts:
  speaker: 'EN-Default'  # 修改这里来更换音色
  language: 'EN'
  device: 'auto'
  speed: 1.0
```

**可用音色：**
- `EN-Default`（英文默认）
- `ZH`（中文）
- 其他根据模型而定

### 6. X-TTS

**配置项：** `speaker_wav`

```yaml
x_tts:
  api_url: 'http://127.0.0.1:8020/tts_to_audio'
  speaker_wav: 'female'  # 修改这里来更换音色
  language: 'en'
```

**音色选项：**
- `female`（女声）
- `male`（男声）
- 或指定具体的 WAV 文件路径

### 7. GPT-SoVITS

**配置项：** `ref_audio_path`

```yaml
gpt_sovits_tts:
  api_url: 'http://127.0.0.1:9880/tts'
  text_lang: 'zh'
  ref_audio_path: '/path/to/reference_audio.wav'  # 修改这里来更换音色
  prompt_lang: 'zh'
  prompt_text: ''
```

**更换音色：**
1. 准备参考音频文件（WAV 格式）
2. 修改 `ref_audio_path` 指向新音频文件
3. 可选：设置 `prompt_text` 为参考音频的文本内容

### 8. Coqui TTS

**配置项：** `model_name` 和 `speaker_wav`

```yaml
coqui_tts:
  model_name: 'tts_models/en/ljspeech/tacotron2-DDC'
  speaker_wav: ''  # 对于多说话人模型，指定说话人音频
  language: 'en'
```

**查看可用模型：**
```bash
tts --list_models
```

### 9. ElevenLabs TTS

**配置项：** `voice_id`

```yaml
elevenlabs_tts:
  api_key: 'your-api-key'
  voice_id: 'your-voice-id'  # 修改这里来更换音色
  model_id: 'eleven_multilingual_v2'
```

**获取 Voice ID：**
1. 登录 [ElevenLabs](https://elevenlabs.io/)
2. 在 Voice Library 中选择或创建音色
3. 复制对应的 Voice ID

### 10. Minimax TTS

**配置项：** `voice_id`

```yaml
minimax_tts:
  group_id: 'your-group-id'
  api_key: 'your-api-key'
  model: 'speech-02-turbo'
  voice_id: 'female-shaonv'  # 修改这里来更换音色
```

**可用音色 ID：**
- `female-shaonv`（少女女声）
- `female-qingxin`（清新女声）
- `male-wennuan`（温暖男声）
- 更多音色请查看 [Minimax 文档](https://platform.minimaxi.com/document)

### 11. SiliconFlow TTS

**配置项：** `default_voice`

```yaml
siliconflow_tts:
  api_url: "https://api.siliconflow.cn/v1/audio/speech"
  api_key: "your-key"
  default_model: "FunAudioLLM/CosyVoice2-0.5B"
  default_voice: "speech:Dreamflowers:5bdstvc39i:xkqldnpasqmoqbakubom your voice name"
```

**格式说明：**
`speech:模型名称:音色ID:您的语音名称`

### 12. Fish API TTS

**配置项：** `reference_id`

```yaml
fish_api_tts:
  api_key: 'your-api-key'
  reference_id: 'your-reference-id'  # 修改这里来更换音色
  latency: 'balanced'
```

**获取 Reference ID：**
访问 [Fish Audio 网站](https://fish.audio/) 获取音色的 reference_id

### 13. Spark TTS

**配置项：** `prompt_wav_upload`（语音克隆）或 `gender`（语音创建）

```yaml
spark_tts:
  api_url: 'http://127.0.0.1:6006/'
  api_name: 'voice_clone'  # 或 'voice_creation'
  prompt_wav_upload: 'https://...'  # 语音克隆时使用
  gender: 'female'  # 语音创建时使用
```

### 14. OpenAI TTS（兼容接口）

**配置项：** `voice`

```yaml
openai_tts:
  model: 'kokoro'
  voice: 'af_sky+af_bella'  # 修改这里来更换音色
  api_key: 'not-needed'
  base_url: 'http://localhost:8880/v1'
```

## 通用提示

1. **修改配置后需要重启服务器**才能生效
2. **某些 TTS 引擎需要先下载模型**才能使用特定音色
3. **API 类 TTS**（如 Azure、ElevenLabs）需要有效的 API 密钥
4. **语音克隆类 TTS**（如 GPT-SoVITS、X-TTS）需要准备参考音频文件

## 测试音色

修改配置后，建议：
1. 重启服务器：`uv run run_server.py`
2. 通过前端界面测试新的音色效果
3. 如果音色不符合预期，可以尝试其他选项或调整相关参数（如 `pitch`、`rate`、`speed` 等）
