# Neon OS Releases
Neon OS releases can be primarily differentiated by a `core` version and
an `image` version, where `core` refers to the repository providing the primary
functionality (i.e. `neon-core` or `neon-nodes`) and `image` refers to code from
the `neon_debos` repository. A particular OS release is identified by a
`build version` string based on the time at which the release was compiled.

## Identifying Updates
Updates are identified as OS releases with the same `core` and a newer 
`build version`.

A `build version` is marked as a beta if either the `core` or the `image` ref
used is a beta (these will always be the same ref in automated builds). 
A device on a beta update track will only update to a newer
beta version; a device on a stable update track will only update to a newer
stable version. If a device changes tracks, it will update to a NEWER release on
the new track, but it will not install an older version by default.
> Note that in practice, any stable update will have first been released to the
> beta track.

## Version Management
Released images are identified in GitHub releases in this repository. The `yaml`
index files may also be used to view release history per-image. Each yaml index
entry has a `version` key that corresponds to a unique build; two builds may have
the same `core` and `image` versions but different build versions based on when
they were created.

### Versioning Scheme
Releases will follow [CalVer](https://calver.org/), so a release version may be
`24.02.14` or `24.02.14b1`. Note that the GitHub beta tags will *not* match the 
associated images' versions for beta versions since each release may relate to a
different `core`.
> i.e. Neon OS tag `24.02.27.b1` may contain `debian-neon-image-24.02.27b1` 
> and Neon OS tag `24.02.27.b2` may contain `debian-node-image-24.02.27b4`.

## Glossary
- `core`: the module/repository providing the primary functionality
- `image`: the framework/repository building the OS image (`neon-debos`)
- `build id`: `recipe`-`platform` string identifier (i.e. `debain-neon-image-rpi4`)
- `build version`: the version identifier for a specific release image
- `release`: a versioned release in the Neon OS repository.
