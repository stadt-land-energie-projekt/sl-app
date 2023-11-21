from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.gdal import GDALException, OGRGeomType
from django.contrib.gis.gdal.field import OFTInteger
from django.contrib.gis.utils.layermapping import LayerMapError, LayerMapping
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import models


class RelatedModelLayerMapping(LayerMapping):
    def check_layer(self):  # noqa: C901
        """
        Check the Layer metadata and ensure that it's compatible with the
        mapping information and model. Unlike previous revisions, there is no
        need to increment through each feature in the Layer.
        """
        # The geometry field of the model is set here.
        # TODO: Support more than one geometry field / model.  However, this
        # depends on the GDAL Driver in use.
        self.geom_field = False
        self.fields = {}

        # Getting lists of the field names and the field types available in
        # the OGR Layer.
        ogr_fields = self.layer.fields
        ogr_field_types = self.layer.field_types

        # Function for determining if the OGR mapping field is in the Layer.
        def check_ogr_fld(ogr_map_fld):
            try:
                idx = ogr_fields.index(ogr_map_fld)
            except ValueError:
                raise LayerMapError('Given mapping OGR field "%s" not found in OGR Layer.' % ogr_map_fld)
            return idx

        # No need to increment through each feature in the model, simply check
        # the Layer metadata against what was given in the mapping dictionary.
        for field_name, ogr_name in self.mapping.items():
            # Ensuring that a corresponding field exists in the model
            # for the given field name in the mapping.
            try:
                model_field = self.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                raise LayerMapError('Given mapping field "%s" not in given Model fields.' % field_name)

            # Getting the string name for the Django field class (e.g., 'PointField').
            fld_name = model_field.__class__.__name__

            if isinstance(model_field, GeometryField):
                if self.geom_field:
                    msg = "LayerMapping does not support more than one GeometryField per model."
                    raise LayerMapError(msg)

                # Getting the coordinate dimension of the geometry field.
                coord_dim = model_field.dim

                try:
                    gtype = OGRGeomType(ogr_name + "25D") if coord_dim == 3 else OGRGeomType(ogr_name)
                except GDALException:
                    raise LayerMapError('Invalid mapping for GeometryField "%s".' % field_name)

                # Making sure that the OGR Layer's Geometry is compatible.
                ltype = self.layer.geom_type
                if not (ltype.name.startswith(gtype.name) or self.make_multi(ltype, model_field)):
                    raise LayerMapError(
                        "Invalid mapping geometry; model has {}{}, "
                        "layer geometry type is {}.".format(fld_name, "(dim=3)" if coord_dim == 3 else "", ltype),
                    )

                # Setting the `geom_field` attribute w/the name of the model field
                # that is a Geometry.  Also setting the coordinate dimension
                # attribute.
                self.geom_field = field_name
                self.coord_dim = coord_dim
                fields_val = model_field
            elif isinstance(model_field, models.ForeignKey):
                if isinstance(ogr_name, dict):
                    # Is every given related model mapping field in the Layer?
                    rel_model = model_field.remote_field.model

                    for rel_name, ogr_field in ogr_name.items():
                        idx = check_ogr_fld(ogr_field)
                        try:
                            rel_model._meta.get_field(rel_name.split("__")[0])
                        except FieldDoesNotExist:
                            raise LayerMapError(
                                f'ForeignKey mapping field "{rel_name}" not in {rel_model.__class__.__name__} fields.',
                            )
                    fields_val = rel_model
                else:
                    msg = "ForeignKey mapping must be of dictionary type."
                    raise TypeError(msg)
            else:
                # Is the model field type supported by LayerMapping?
                if model_field.__class__ not in self.FIELD_TYPES:
                    raise LayerMapError('Django field type "%s" has no OGR mapping (yet).' % fld_name)

                # Is the OGR field in the Layer?
                if ogr_name == "FID":
                    ogr_field = OFTInteger
                else:
                    idx = check_ogr_fld(ogr_name)
                    ogr_field = ogr_field_types[idx]

                # Can the OGR field type be mapped to the Django field type?
                if not issubclass(ogr_field, self.FIELD_TYPES[model_field.__class__]):
                    raise LayerMapError(
                        f'OGR field "{ogr_field}" (of type {ogr_field.__name__}) '
                        f"cannot be mapped to Django {fld_name}.",
                    )
                fields_val = model_field

            self.fields[field_name] = fields_val

    def verify_fk(self, feat, rel_model, rel_mapping):
        """
        Given an OGR Feature, the related model and its dictionary mapping,
        retrieve the related model for the ForeignKey mapping.
        """
        # TODO: It is expensive to retrieve a model for every record --
        #  explore if an efficient mechanism exists for caching related
        #  ForeignKey models.

        # Constructing and verifying the related model keyword arguments.
        fk_kwargs = {}
        for field_name, ogr_name in rel_mapping.items():
            fk_kwargs[field_name] = self.verify_ogr_field(
                feat[ogr_name],
                rel_model._meta.get_field(field_name.split("__")[0]),
            )

        # Attempting to retrieve and return the related model.
        try:
            return rel_model.objects.using(self.using).get(**fk_kwargs)
        except ObjectDoesNotExist:
            return None

    # Keyword argument retrieval routines ####
    def feature_kwargs(self, feat):
        """
        Given an OGR Feature, return a dictionary of keyword arguments for
        constructing the mapped model.
        """
        # The keyword arguments for model construction.
        kwargs = {}

        # Incrementing through each model field and OGR field in the
        # dictionary mapping.
        for field_name, ogr_name in self.mapping.items():
            model_field = self.fields[field_name]

            if isinstance(model_field, GeometryField):
                # Verify OGR geometry.
                try:
                    val = self.verify_geom(feat.geom, model_field)
                except GDALException:
                    msg = "Could not retrieve geometry from feature."
                    raise LayerMapError(msg)
            elif isinstance(model_field, models.base.ModelBase):
                # The related _model_, not a field was passed in -- indicating
                # another mapping for the related Model.
                val = self.verify_fk(feat, model_field, ogr_name)
            elif ogr_name == "FID":
                val = feat.fid
            else:
                val = self.verify_ogr_field(feat[ogr_name], model_field)

            # Setting the keyword arguments for the field name with the
            # value obtained above.
            kwargs[field_name] = val

        return kwargs
