# music-mix — song mixing/mastering pipeline (Nov 2026)

Used for the user's own R&B song (stems from Google Drive: Drums, Bass, Others + 5 vocal tracks).
Audio files are not stored here (too large); only the scripts.

- `tunelib.py` — note-level pitch correction (Praat/parselmouth): each sung note is shifted as a
  whole toward the nearest scale note, vibrato and slides are kept; notes more than 50 cents from
  any scale note are left alone.
- `mix2.py <stems_dir> <work_dir> <lib_dir> <vocal_dB_vs_beat>` — tunes vocals, per-stem EQ /
  compression / de-essing, reverb + delay sends, balance, writes `premaster.wav`.
- `master2.py <work_dir> <target_LUFS>` — glue compression, soft clip, true-peak limiter.
- `tuning_report.json` — every corrected note (time, length, target note, deviation in cents).

Needs: `pip install scipy soundfile pedalboard pyloudnorm praat-parselmouth librosa gdown`
(and `demucs` + CPU torch when the user sends only a single mixed file).
