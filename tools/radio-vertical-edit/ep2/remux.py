import sys,os,subprocess
sys.argv=['x']
import compose as C
C.build_audio()
B=C.BASE
subprocess.run(['ffmpeg','-v','error','-y','-i',os.path.join(B,'mix_raw.wav'),'-af','acompressor=threshold=-22dB:ratio=3:attack=6:release=180:makeup=2,lowpass=f=15000,loudnorm=I=-14:TP=-1.5:LRA=8','-ar','48000',os.path.join(B,'mix.wav')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',os.path.join(B,'video_only.mp4'),'-i',os.path.join(B,'mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest',os.path.join(B,'ep2_v3.mp4')],check=True)
print('ok')
