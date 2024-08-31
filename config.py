# config.py

DEFAULT_URL = "streamingpro.es"
DEFAULT_PORT = "6000"
DEFAULT_LATENCY = "200"

def build_srt_url(url, port, latency, streamid):
    url = url if url else DEFAULT_URL
    port = port if port else DEFAULT_PORT
    latency = latency if latency else DEFAULT_LATENCY
    
    srt_url = f"srt://{url}:{port}/?mode=caller&latency={latency}"
    
    if streamid:
        srt_url += f"&streamid={streamid}"
        
    return srt_url
