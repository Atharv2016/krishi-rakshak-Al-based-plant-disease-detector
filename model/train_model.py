"""Train MobileNetV2 on Tomato, Potato and Grape PlantVillage folders."""
from pathlib import Path
import json, os, random
import tensorflow as tf

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv('KRISHI_DATA_DIR', ROOT / 'dataset' / 'PlantVillage'))
OUT_DIR = ROOT / 'model'
IMG_SIZE = (224, 224)
BATCH_SIZE = int(os.getenv('KRISHI_BATCH_SIZE', '32'))
SEED = 42
CROPS = {'Tomato', 'Potato', 'Grape'}
VALID_EXT = {'.jpg', '.jpeg', '.png'}


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f'Dataset folder not found: {DATA_DIR}\nSee README.md for setup.')
    class_dirs = sorted(p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.split('___', 1)[0] in CROPS)
    if len(class_dirs) < 2:
        raise SystemExit('No usable class folders found. Expected folders such as Tomato___Early_blight.')
    class_names = [p.name for p in class_dirs]
    train_paths, train_labels, val_paths, val_labels = [], [], [], []
    rng = random.Random(SEED)
    for label, folder in enumerate(class_dirs):
        files = [p for p in folder.iterdir() if p.suffix.lower() in VALID_EXT]
        rng.shuffle(files)
        if len(files) < 2:
            print(f'WARNING: too few images in {folder.name}; skipping class.')
            continue
        split = max(1, int(len(files) * 0.15))
        val_files, train_files = files[:split], files[split:]
        train_paths.extend(str(p) for p in train_files); train_labels.extend([label] * len(train_files))
        val_paths.extend(str(p) for p in val_files); val_labels.extend([label] * len(val_files))
        print(f'{folder.name}: {len(train_files)} train, {len(val_files)} validation')
    if len(set(train_labels)) < 2 or not val_paths:
        raise SystemExit('Need at least two classes with enough images for train/validation splits.')
    # Re-index classes in case a too-small folder was skipped.
    used_old = sorted(set(train_labels) | set(val_labels))
    remap = {old: new for new, old in enumerate(used_old)}
    class_names = [class_names[i] for i in used_old]
    train_labels = [remap[x] for x in train_labels]; val_labels = [remap[x] for x in val_labels]

    def read_image(path, label):
        raw = tf.io.read_file(path)
        image = tf.io.decode_image(raw, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, IMG_SIZE)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(tf.cast(image, tf.float32))
        return image, tf.one_hot(label, len(class_names))

    def dataset(paths, labels, training):
        ds = tf.data.Dataset.from_tensor_slices((paths, labels))
        if training: ds = ds.shuffle(min(len(paths), 10000), seed=SEED)
        ds = ds.map(read_image, num_parallel_calls=tf.data.AUTOTUNE)
        if training:
            aug = tf.keras.Sequential([tf.keras.layers.RandomFlip('horizontal'), tf.keras.layers.RandomRotation(0.08), tf.keras.layers.RandomZoom(0.1)])
            ds = ds.map(lambda x, y: (aug(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
        return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    train_ds = dataset(train_paths, train_labels, True)
    val_ds = dataset(val_paths, val_labels, False)
    base = tf.keras.applications.MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights='imagenet')
    base.trainable = False
    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(len(class_names), activation='softmax')(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss='categorical_crossentropy', metrics=['accuracy'])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    callbacks = [tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=4, restore_best_weights=True),
                 tf.keras.callbacks.ModelCheckpoint(OUT_DIR / 'plant_disease_model.keras', monitor='val_accuracy', save_best_only=True)]
    print('Training classifier head...')
    model.fit(train_ds, validation_data=val_ds, epochs=int(os.getenv('KRISHI_HEAD_EPOCHS', '12')), callbacks=callbacks)
    base.trainable = True
    for layer in base.layers[:-30]: layer.trainable = False
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='categorical_crossentropy', metrics=['accuracy'])
    print('Fine-tuning final MobileNetV2 layers...')
    model.fit(train_ds, validation_data=val_ds, epochs=int(os.getenv('KRISHI_FINE_EPOCHS', '5')), callbacks=callbacks)
    best = tf.keras.models.load_model(OUT_DIR / 'plant_disease_model.keras')
    loss, accuracy = best.evaluate(val_ds, verbose=0)
    (OUT_DIR / 'class_names.json').write_text(json.dumps(class_names, indent=2), encoding='utf-8')
    report = {'validation_loss': float(loss), 'validation_accuracy': float(accuracy), 'classes': class_names,
              'train_images': len(train_paths), 'validation_images': len(val_paths),
              'note': 'Validation results may not represent real-world farm performance.'}
    (OUT_DIR / 'training_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
