#!/usr/bin/env python3
"""
Video Glitch Frame Remover
Identifies and removes a specific frame that repeats abnormally throughout a video.
"""

import cv2
import numpy as np
from collections import defaultdict
import argparse
from pathlib import Path
import ffmpeg
import tempfile


def compute_frame_hash(frame):
    """
    Compute a perceptual hash for a frame.
    Uses average hash method for faster computation.
    """
    # Resize to 8x8 for hash computation
    resized = cv2.resize(frame, (8, 8), interpolation=cv2.INTER_AREA)
    # Convert to grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # Compute average
    avg = gray.mean()
    # Create hash based on values above/below average
    hash_value = 0
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_value |= 1 << (i * 8 + j)
    return hash_value


def hamming_distance(hash1, hash2):
    """Calculate Hamming distance between two hashes."""
    return bin(hash1 ^ hash2).count('1')


def find_glitch_frame(video_path, sample_rate=30, similarity_threshold=5):
    """
    Identify the glitch frame by finding abnormally repeated frames.
    
    Args:
        video_path: Path to the input video
        sample_rate: Sample every Nth frame for efficiency (1 = all frames)
        similarity_threshold: Max Hamming distance to consider frames identical
    
    Returns:
        The hash of the glitch frame, or None if not found
    """
    print(f"Analyzing video: {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Total frames: {total_frames}, FPS: {fps}")
    
    frame_hashes = []
    frame_indices = []
    frame_count = 0
    
    # Sample frames and compute hashes
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % sample_rate == 0:
            frame_hash = compute_frame_hash(frame)
            frame_hashes.append(frame_hash)
            frame_indices.append(frame_count)
        
        frame_count += 1
        if frame_count % 1000 == 0:
            print(f"Processed {frame_count}/{total_frames} frames...")
    
    cap.release()
    print(f"Sampled {len(frame_hashes)} frames")
    
    # Group similar frames together
    hash_groups = defaultdict(list)
    for idx, frame_hash in enumerate(frame_hashes):
        # Find if this hash belongs to an existing group
        found_group = False
        for group_hash in hash_groups.keys():
            if hamming_distance(frame_hash, group_hash) <= similarity_threshold:
                hash_groups[group_hash].append(frame_indices[idx])
                found_group = True
                break
        
        if not found_group:
            hash_groups[frame_hash].append(frame_indices[idx])
    
    # Find frames that appear suspiciously often
    # A glitch frame appears at regular intervals, not consecutively
    suspicious_frames = {}
    for hash_val, indices in hash_groups.items():
        if len(indices) >= 3:  # Appears at least 3 times
            # Check if appearances are spread out (not consecutive)
            gaps = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
            avg_gap = np.mean(gaps)
            
            # If average gap is significant, it's likely the glitch
            if avg_gap > fps * 2:  # Appears at least 2 seconds apart
                suspicious_frames[hash_val] = {
                    'count': len(indices),
                    'indices': indices,
                    'avg_gap': avg_gap
                }
    
    if not suspicious_frames:
        print("No glitch frame detected!")
        return None
    
    # Select the most suspicious one
    glitch_hash = max(suspicious_frames.keys(), 
                     key=lambda h: suspicious_frames[h]['count'])
    
    glitch_info = suspicious_frames[glitch_hash]
    print(f"\nGlitch frame detected!")
    print(f"  Appears {glitch_info['count']} times")
    print(f"  Average gap: {glitch_info['avg_gap']:.1f} frames "
          f"({glitch_info['avg_gap']/fps:.1f} seconds)")
    print(f"  Frame indices (sampled): {glitch_info['indices'][:10]}...")
    
    return glitch_hash


def export_frame(video_path, frame_index, output_path=None):
    """
    Export a specific frame or range of frames from a video as image files.
    
    Args:
        video_path: Path to the input video
        frame_index: Index of the frame to export (0-based), or tuple (start, end) for range
        output_path: Path to save the image (default: frame_{index}.png)
                     For ranges, this is used as a prefix (ignored if None)
    
    Returns:
        Path to the saved image file, or list of paths for frame ranges
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_path_obj = Path(video_path)
    
    # Check if frame_index is a tuple (range)
    if isinstance(frame_index, tuple):
        start_frame, end_frame = frame_index
        
        # Validate frame range
        if start_frame < 0 or start_frame >= total_frames:
            cap.release()
            raise ValueError(f"Start frame {start_frame} is out of range (0-{total_frames-1})")
        if end_frame < 0 or end_frame >= total_frames:
            cap.release()
            raise ValueError(f"End frame {end_frame} is out of range (0-{total_frames-1})")
        if start_frame > end_frame:
            cap.release()
            raise ValueError(f"Start frame {start_frame} must be <= end frame {end_frame}")
        
        # Export all frames in range
        exported_paths = []
        for idx in range(start_frame, end_frame + 1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if not ret:
                cap.release()
                raise RuntimeError(f"Failed to read frame {idx}")
            
            # Determine output path for this frame
            if output_path is None:
                frame_output = video_path_obj.parent / f"frame_{idx}.png"
            else:
                output_path_obj = Path(output_path)
                frame_output = output_path_obj.parent / f"{output_path_obj.stem}_{idx}.png"
            
            # Save the frame as PNG (lossless)
            success = cv2.imwrite(str(frame_output), frame)
            
            if not success:
                cap.release()
                raise RuntimeError(f"Failed to save frame to {frame_output}")
            
            exported_paths.append(frame_output)
            print(f"Frame {idx} exported to: {frame_output}")
        
        cap.release()
        print(f"Exported {len(exported_paths)} frames from {start_frame} to {end_frame}")
        return exported_paths
    
    else:
        # Single frame export (original behavior)
        if frame_index < 0 or frame_index >= total_frames:
            cap.release()
            raise ValueError(f"Frame index {frame_index} is out of range (0-{total_frames-1})")
        
        # Set the video to the desired frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # Read the frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise RuntimeError(f"Failed to read frame {frame_index}")
        
        # Determine output path
        if output_path is None:
            output_path = video_path_obj.parent / f"frame_{frame_index}.png"
        else:
            output_path = Path(output_path)
        
        # Save the frame as PNG (lossless)
        success = cv2.imwrite(str(output_path), frame)
        
        if not success:
            raise RuntimeError(f"Failed to save frame to {output_path}")
        
        print(f"Frame {frame_index} exported to: {output_path}")
        return output_path


def remove_glitch_frames(input_path, output_path, glitch_hash, similarity_threshold=5):
    """
    Create a new video with glitch frames removed.
    
    Args:
        input_path: Path to input video
        output_path: Path to output video
        glitch_hash: Hash of the glitch frame to remove
        similarity_threshold: Max Hamming distance to consider frames identical
    """
    print(f"\nRemoving glitch frames...")
    
    # First, extract audio from the original video
    temp_audio = None
    has_audio = False
    
    try:
        # Check if video has audio using ffmpeg.probe
        probe = ffmpeg.probe(input_path.as_posix())
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        has_audio = len(audio_streams) > 0
        
        if has_audio:
            print("Extracting audio from original video...")
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.aac')
            temp_audio.close()
            
            # Extract audio using ffmpeg-python
            (
                ffmpeg
                .input(str(input_path))
                .output(temp_audio.name, vn=None, acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"Audio extracted to temporary file")
    except ffmpeg.Error as e:
        print(f"Warning: Could not extract audio: {e.stderr.decode() if e.stderr else str(e)}")
        return
        has_audio = False
    
    cap = cv2.VideoCapture(str(input_path))
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create temporary output for video without audio
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video.close()
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video.name, fourcc, fps, (width, height))
    
    frames_removed = 0
    frames_kept = 0
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Check if this frame matches the glitch
        frame_hash = compute_frame_hash(frame)
        distance = hamming_distance(frame_hash, glitch_hash)
        
        if distance <= similarity_threshold:
            # Export the glitch frame
            export_path = Path(output_path).parent / f"removed_{frames_removed}.png"
            cv2.imwrite(str(export_path), frame)
            # Skip this frame (it's the glitch)
            frames_removed += 1
        else:
            # Keep this frame
            out.write(frame)
            frames_kept += 1
        
        frame_count += 1
        if frame_count % 1000 == 0:
            print(f"Processed {frame_count}/{total_frames} frames "
                  f"(removed: {frames_removed}, kept: {frames_kept})...")
    
    cap.release()
    out.release()
    
    # Mux audio back with the processed video
    if has_audio:
        try:
            print("\nMuxing audio back into the video...")
            # Mux video and audio using ffmpeg-python
            video_stream = ffmpeg.input(temp_video.name)
            audio_stream = ffmpeg.input(temp_audio.name)
            
            (
                ffmpeg
                .output(video_stream, audio_stream, str(output_path), 
                        vcodec='copy', acodec='aac', strict='experimental')
                .overwrite_output()
                .run(quiet=True)
            )
            print("Audio successfully added to output video")
            
            # Clean up temporary files
            Path(temp_audio.name).unlink(missing_ok=True)
            Path(temp_video.name).unlink(missing_ok=True)
        except ffmpeg.Error as e:
            print(f"Warning: Failed to mux audio. Saving video without audio...")
            print(f"Error: {e.stderr.decode() if e.stderr else str(e)}")
            # Copy temp video to output if muxing fails
            import shutil
            shutil.copy(temp_video.name, output_path)
            Path(temp_video.name).unlink(missing_ok=True)
            if temp_audio:
                Path(temp_audio.name).unlink(missing_ok=True)
    else:
        # No audio, just move the temp video to output
        import shutil
        shutil.move(temp_video.name, str(output_path))
    
    print(f"\nComplete!")
    print(f"  Total frames processed: {frame_count}")
    print(f"  Frames removed: {frames_removed}")
    print(f"  Frames kept: {frames_kept}")
    print(f"  Output saved to: {output_path}")


def compute_glitch_hash_from_index(video_path, frame_index):
    """
    Compute the hash of a specific frame to use as the glitch reference.
    
    Args:
        video_path: Path to the input video
        frame_index: Index of the glitched frame (0-based)
    
    Returns:
        Hash of the glitched frame, or None if an error occurred
    """
    print(f"Using specified glitched frame at index: {frame_index}")
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"Error: Cannot open video file: {video_path}")
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_index < 0 or frame_index >= total_frames:
        print(f"Error: Frame index {frame_index} is out of range (0-{total_frames-1})")
        cap.release()
        return None
    
    # Read the specified frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"Error: Failed to read frame {frame_index}")
        return None
    
    # Compute hash of the glitched frame
    glitch_hash = compute_frame_hash(frame)
    print(f"Computed hash for glitched frame {frame_index}")
    
    return glitch_hash


def remove_specific_frames(input_path, output_path, frame_indices):
    """
    Create a new video with specific frames removed by their indices.
    
    Args:
        input_path: Path to input video
        output_path: Path to output video
        frame_indices: Set of frame indices to remove (0-based)
    """
    print(f"\nRemoving {len(frame_indices)} specific frames...")
    
    # First, extract audio from the original video
    temp_audio = None
    has_audio = False
    
    try:
        # Check if video has audio using ffmpeg.probe
        probe = ffmpeg.probe(input_path.as_posix())
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        has_audio = len(audio_streams) > 0
        
        if has_audio:
            print("Extracting audio from original video...")
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.aac')
            temp_audio.close()
            
            # Extract audio using ffmpeg-python
            (
                ffmpeg
                .input(str(input_path))
                .output(temp_audio.name, vn=None, acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"Audio extracted to temporary file")
    except ffmpeg.Error as e:
        print(f"Warning: Could not extract audio: {e.stderr.decode() if e.stderr else str(e)}")
        has_audio = False
    
    cap = cv2.VideoCapture(str(input_path))
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create temporary output for video without audio
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video.close()
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video.name, fourcc, fps, (width, height))
    
    frames_removed = 0
    frames_kept = 0
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Check if this frame should be removed
        if frame_count in frame_indices:
            # Export the removed frame
            export_path = Path(output_path).parent / f"removed_{frame_count}.png"
            cv2.imwrite(str(export_path), frame)
            frames_removed += 1
        else:
            # Keep this frame
            out.write(frame)
            frames_kept += 1
        
        frame_count += 1
        if frame_count % 1000 == 0:
            print(f"Processed {frame_count}/{total_frames} frames "
                  f"(removed: {frames_removed}, kept: {frames_kept})...")
    
    cap.release()
    out.release()
    
    # Mux audio back with the processed video
    if has_audio:
        try:
            print("\nMuxing audio back into the video...")
            # Mux video and audio using ffmpeg-python
            video_stream = ffmpeg.input(temp_video.name)
            audio_stream = ffmpeg.input(temp_audio.name)
            
            (
                ffmpeg
                .output(video_stream, audio_stream, str(output_path), 
                        vcodec='copy', acodec='aac', strict='experimental')
                .overwrite_output()
                .run(quiet=True)
            )
            print("Audio successfully added to output video")
            
            # Clean up temporary files
            Path(temp_audio.name).unlink(missing_ok=True)
            Path(temp_video.name).unlink(missing_ok=True)
        except ffmpeg.Error as e:
            print(f"Warning: Failed to mux audio. Saving video without audio...")
            print(f"Error: {e.stderr.decode() if e.stderr else str(e)}")
            # Copy temp video to output if muxing fails
            import shutil
            shutil.copy(temp_video.name, output_path)
            Path(temp_video.name).unlink(missing_ok=True)
            if temp_audio:
                Path(temp_audio.name).unlink(missing_ok=True)
    else:
        # No audio, just move the temp video to output
        import shutil
        shutil.move(temp_video.name, str(output_path))
    
    print(f"\nComplete!")
    print(f"  Total frames processed: {frame_count}")
    print(f"  Frames removed: {frames_removed}")
    print(f"  Frames kept: {frames_kept}")
    print(f"  Output saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Remove glitch frames from a video file"
    )
    parser.add_argument(
        "input_video",
        help="Path to the input video file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output video file (default: input_fixed.mp4)"
    )
    parser.add_argument(
        "-s", "--sample-rate",
        type=int,
        default=30,
        help="Sample every Nth frame for detection (default: 30)"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=5,
        help="Similarity threshold for frame matching (default: 5)"
    )
    parser.add_argument(
        "--glitched-frame",
        type=int,
        metavar="INDEX",
        help="Index of a known glitched frame (0-based). When provided, skips detection and uses this frame as the glitch reference."
    )
    parser.add_argument(
        "--remove",
        type=str,
        metavar="INDICES",
        help="Comma-separated list of frame indices to remove (e.g., 279,385,412). Removes only these exact frames."
    )
    parser.add_argument(
        "--export-start",
        type=int,
        metavar="INDEX",
        help="Export frame(s) starting from this index (0-based). Use with --export-end for range, or alone for single frame."
    )
    parser.add_argument(
        "--export-end",
        type=int,
        metavar="INDEX",
        help="Export frame(s) ending at this index (0-based, inclusive). Must be used with --export-start."
    )
    parser.add_argument(
        "--export-output",
        help="Output path for exported frame(s) (default: frame_INDEX.png)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_video)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return
    
    # Handle frame export mode
    if args.export_start is not None:
        try:
            # Determine if we're exporting a range or single frame
            if args.export_end is not None:
                # Export range
                frame_index = (args.export_start, args.export_end)
            else:
                # Export single frame
                frame_index = args.export_start
            
            export_frame(input_path, frame_index, args.export_output)
        except Exception as e:
            print(f"Error exporting frame(s): {e}")
            import traceback
            traceback.print_exc()
        return
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_fixed.mp4"
    
    try:
        # Handle --remove mode (remove specific frame indices)
        if args.remove:
            # Parse comma-separated frame indices
            try:
                frame_indices = set(int(idx.strip()) for idx in args.remove.split(','))
            except ValueError:
                print(f"Error: Invalid frame indices in --remove argument. Use comma-separated integers.")
                return
            
            print(f"Removing {len(frame_indices)} specific frames: {sorted(frame_indices)[:10]}{'...' if len(frame_indices) > 10 else ''}")
            remove_specific_frames(input_path, output_path, frame_indices)
            return
        
        # Step 1: Find or compute the glitch frame hash
        if args.glitched_frame is not None:
            # User specified a known glitched frame - compute its hash directly
            glitch_hash = compute_glitch_hash_from_index(input_path, args.glitched_frame)
            if glitch_hash is None:
                return
        else:
            # Automatically detect the glitch frame
            glitch_hash = find_glitch_frame(
                input_path, 
                sample_rate=args.sample_rate,
                similarity_threshold=args.threshold
            )
            
            if glitch_hash is None:
                print("No glitch frame found. Video may be fine.")
                return
        
        # Step 2: Remove glitch frames
        remove_glitch_frames(
            input_path, 
            output_path, 
            glitch_hash,
            similarity_threshold=args.threshold
        )
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
