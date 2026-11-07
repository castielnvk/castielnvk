use deep_filter_rt::tract::DfTract;
use ndarray::Array2;
use std::io::{Read, Write};
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let lim: f32 = a[3].parse().unwrap();
    let mut buf = Vec::new();
    std::fs::File::open(&a[1]).unwrap().read_to_end(&mut buf).unwrap();
    let x: Vec<f32> = buf.chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect();
    let mut df = DfTract::default();
    df.set_atten_lim(lim);
    let hop = df.hop_size;
    let delay = df.delay();
    eprintln!("hop {} delay {}", hop, delay);
    let n = x.len();
    let mut padded = x.clone();
    padded.extend(std::iter::repeat(0.0).take(delay + hop));
    let mut out: Vec<f32> = Vec::with_capacity(padded.len());
    let mut lsnr = Vec::new();
    for ch in padded.chunks(hop) {
        if ch.len() < hop { break; }
        let noisy = Array2::from_shape_vec((1, hop), ch.to_vec()).unwrap();
        let mut enh = Array2::<f32>::zeros((1, hop));
        let s = df.process(noisy.view(), enh.view_mut()).unwrap();
        lsnr.push(s);
        out.extend(enh.iter());
    }
    let out = &out[delay..delay + n];
    let mut f = std::fs::File::create(&a[2]).unwrap();
    for v in out { f.write_all(&v.to_le_bytes()).unwrap(); }
    eprintln!("frames {}", lsnr.len());
}
