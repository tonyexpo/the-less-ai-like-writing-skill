The 2.4 release changes how we cache parsed configs.

Before, every worker re-parsed `config.yaml` on each request. On the staging box that was 11ms per request, most of it in YAML parsing. We now parse once at boot and hold the result in a module-level dict.

Two things to watch for. The config is no longer re-read on SIGHUP, so a deploy is required to pick up changes. And if you mutate the returned dict you will corrupt it for every later caller, because it is the same object. We considered returning a deep copy and decided the copy cost defeated the point.

Median request time on staging dropped to 4ms. The p99 barely moved, which suggests the tail is dominated by something else. I have not chased that yet.
