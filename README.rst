Salt Masterless Preparer
========================

This project defines a structure that can be used to define a salt masterless
deployment meant to be used with something like packer.

masterless.yml
--------------

One of the limitations with salt masterless is that minions (at this time)
cannot actually download formulas using gitfs. So this is a quick script around
that.

The configuration file::
    
    formulas:
      - git-url-a
      - git-url-b:
        - branch:
        - tag:
        - commit:

The configuration is pretty simple. Just outline the git urls you need and you
can specify specific tags/branches/commits.

The masterless preparer takes a path as input and outputs a temporary directory
with all of the formulas and pillars joined. All the salt states collected.
