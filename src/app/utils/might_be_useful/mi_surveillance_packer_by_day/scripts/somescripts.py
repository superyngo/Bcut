ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c copy output.mp4
# speedup with itsscale
# ffmpeg.input(
#     input_file,
#     itsscale=f"{1/multiple}",
# ).output(
#     str(temp_output_file),
#     vcodec="copy",
#     acodec="copy",
#     map=0,
#     **othertags,
# )
