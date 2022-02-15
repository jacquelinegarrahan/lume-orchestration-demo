FROM continuumio/miniconda3 AS build

# Create environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a  enviornment in /venv:
RUN conda-pack -n  astra-impact-example -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# Fix paths, will be same in final image so this is fine
RUN /venv/bin/conda-unpack


# No longer need conda, just the packed python
FROM debian:buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# When image is run, run the code with the environment
# activated:

COPY _entrypoint.sh /usr/local/bin/_entrypoint.sh
RUN chmod +x /usr/local/bin/_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]