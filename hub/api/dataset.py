from hub.util.exceptions import DatasetHandlerError
from hub.util.storage import get_storage_and_cache_chain
from typing import Optional, Union
from hub.constants import DEFAULT_LOCAL_CACHE_SIZE, DEFAULT_MEMORY_CACHE_SIZE, MB
from hub.core.dataset import Dataset
from hub.util.keys import dataset_exists
from hub.util.bugout_reporter import hub_reporter
from hub.client.client import HubBackendClient


class dataset:
    def __new__(
        cls,
        path: str,
        read_only: bool = False,
        overwrite: bool = False,
        public: bool = True,
        memory_cache_size: int = DEFAULT_MEMORY_CACHE_SIZE,
        local_cache_size: int = DEFAULT_LOCAL_CACHE_SIZE,
        creds: Optional[dict] = None,
        token: Optional[str] = None,
    ):
        """Returns a Dataset object referencing either a new or existing dataset.

        Important:
            Using `overwrite` will delete all of your data if it exists! Be very careful when setting this parameter.

        Args:
            path (str): The full path to the dataset. Can be:-
                - a Hub cloud path of the form hub://username/datasetname. To write to Hub cloud datasets, ensure that you are logged in to Hub (use 'activeloop login' from command line)
                - an s3 path of the form s3://bucketname/path/to/dataset. Credentials are required in either the environment or passed to the creds argument.
                - a local file system path of the form ./path/to/dataset or ~/path/to/dataset or path/to/dataset.
                - a memory path of the form mem://path/to/dataset which doesn't save the dataset but keeps it in memory instead. Should be used only for testing as it does not persist.
            read_only (bool): Opens dataset in read only mode if this is passed as True. Defaults to False.
                Datasets stored on Hub cloud that your account does not have write access to will automatically open in read mode.
            overwrite (bool): WARNING: If set to True this overwrites the dataset if it already exists. This can NOT be undone! Defaults to False.
            public (bool): Defines if the dataset will have public access. Applicable only if Hub cloud storage is used and a new Dataset is being created. Defaults to True.
            memory_cache_size (int): The size of the memory cache to be used in MB.
            local_cache_size (int): The size of the local filesystem cache to be used in MB.
            creds (dict, optional): A dictionary containing credentials used to access the dataset at the path.
                This takes precedence over credentials present in the environment. Currently only works with s3 paths.
                It supports 'aws_access_key_id', 'aws_secret_access_key', 'aws_session_token', 'endpoint_url' and 'region' as keys.
            token (str, optional): Activeloop token, used for fetching credentials for Hub datasets. This is optional, tokens are normally autogenerated.

        Returns:
            Dataset object created using the arguments provided.
        """
        if creds is None:
            creds = {}
        storage, cache_chain = get_storage_and_cache_chain(
            path=path,
            read_only=read_only,
            creds=creds,
            token=token,
            memory_cache_size=memory_cache_size,
            local_cache_size=local_cache_size,
        )
        if overwrite and dataset_exists(storage):
            storage.clear()
        read_only = storage.read_only

        hub_reporter.feature_report(feature_name="dataset", parameters={})

        return Dataset(
            storage=cache_chain, read_only=read_only, public=public, token=token
        )

    @staticmethod
    @hub_reporter.record_call
    def empty(
        path: str,
        overwrite: bool = False,
        public: Optional[bool] = True,
        memory_cache_size: int = DEFAULT_MEMORY_CACHE_SIZE,
        local_cache_size: int = DEFAULT_LOCAL_CACHE_SIZE,
        creds: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> Dataset:
        """Creates an empty dataset

        Important:
            Using `overwrite` will delete all of your data if it exists! Be very careful when setting this parameter.

        Args:
            path (str): The full path to the dataset. Can be:-
                - a Hub cloud path of the form hub://username/datasetname. To write to Hub cloud datasets, ensure that you are logged in to Hub (use 'activeloop login' from command line)
                - an s3 path of the form s3://bucketname/path/to/dataset. Credentials are required in either the environment or passed to the creds argument.
                - a local file system path of the form ./path/to/dataset or ~/path/to/dataset or path/to/dataset.
                - a memory path of the form mem://path/to/dataset which doesn't save the dataset but keeps it in memory instead. Should be used only for testing as it does not persist.
            overwrite (bool): WARNING: If set to True this overwrites the dataset if it already exists. This can NOT be undone! Defaults to False.
            public (bool, optional): Defines if the dataset will have public access. Applicable only if Hub cloud storage is used and a new Dataset is being created. Defaults to True.
            memory_cache_size (int): The size of the memory cache to be used in MB.
            local_cache_size (int): The size of the local filesystem cache to be used in MB.
            creds (dict, optional): A dictionary containing credentials used to access the dataset at the path.
                This takes precedence over credentials present in the environment. Currently only works with s3 paths.
                It supports 'aws_access_key_id', 'aws_secret_access_key', 'aws_session_token', 'endpoint_url' and 'region' as keys.
            token (str, optional): Activeloop token, used for fetching credentials for Hub datasets. This is optional, tokens are normally autogenerated.

        Returns:
            Dataset object created using the arguments provided.

        Raises:
            DatasetHandlerError: If a Dataset already exists at the given path and overwrite is False.
        """
        if creds is None:
            creds = {}
        storage, cache_chain = get_storage_and_cache_chain(
            path=path,
            read_only=False,
            creds=creds,
            token=token,
            memory_cache_size=memory_cache_size,
            local_cache_size=local_cache_size,
        )

        if overwrite and dataset_exists(storage):
            storage.clear()
        elif dataset_exists(storage):
            raise DatasetHandlerError(
                f"A dataset already exists at the given path ({path}). If you want to create a new empty dataset, either specify another path or use overwrite=True. If you want to load the dataset that exists at this path, use dataset.load() or dataset() instead."
            )
        read_only = storage.read_only
        return Dataset(
            storage=cache_chain, read_only=read_only, public=public, token=token
        )

    @staticmethod
    @hub_reporter.record_call
    def load(
        path: str,
        read_only: bool = False,
        overwrite: bool = False,
        public: Optional[bool] = True,
        memory_cache_size: int = DEFAULT_MEMORY_CACHE_SIZE,
        local_cache_size: int = DEFAULT_LOCAL_CACHE_SIZE,
        creds: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> Dataset:
        """Loads an existing dataset

        Important:
            Using `overwrite` will delete all of your data if it exists! Be very careful when setting this parameter.

        Args:
            path (str): The full path to the dataset. Can be:-
                - a Hub cloud path of the form hub://username/datasetname. To write to Hub cloud datasets, ensure that you are logged in to Hub (use 'activeloop login' from command line)
                - an s3 path of the form s3://bucketname/path/to/dataset. Credentials are required in either the environment or passed to the creds argument.
                - a local file system path of the form ./path/to/dataset or ~/path/to/dataset or path/to/dataset.
                - a memory path of the form mem://path/to/dataset which doesn't save the dataset but keeps it in memory instead. Should be used only for testing as it does not persist.
            read_only (bool): Opens dataset in read only mode if this is passed as True. Defaults to False.
                Datasets stored on Hub cloud that your account does not have write access to will automatically open in read mode.
            overwrite (bool): WARNING: If set to True this overwrites the dataset if it already exists. This can NOT be undone! Defaults to False.
            public (bool, optional): Defines if the dataset will have public access. Applicable only if Hub cloud storage is used and a new Dataset is being created. Defaults to True.
            memory_cache_size (int): The size of the memory cache to be used in MB.
            local_cache_size (int): The size of the local filesystem cache to be used in MB.
            creds (dict, optional): A dictionary containing credentials used to access the dataset at the path.
                This takes precedence over credentials present in the environment. Currently only works with s3 paths.
                It supports 'aws_access_key_id', 'aws_secret_access_key', 'aws_session_token', 'endpoint_url' and 'region' as keys.
            token (str, optional): Activeloop token, used for fetching credentials for Hub datasets. This is optional, tokens are normally autogenerated.

        Returns:
            Dataset object created using the arguments provided.

        Raises:
            DatasetHandlerError: If a Dataset does not exist at the given path.
        """
        if creds is None:
            creds = {}

        storage, cache_chain = get_storage_and_cache_chain(
            path=path,
            read_only=read_only,
            creds=creds,
            token=token,
            memory_cache_size=memory_cache_size,
            local_cache_size=local_cache_size,
        )

        if not dataset_exists(storage):
            raise DatasetHandlerError(
                f"A Hub dataset does not exist at the given path ({path}). Check the path provided or in case you want to create a new dataset, use dataset.empty() or dataset()."
            )
        if overwrite:
            storage.clear()
        read_only = storage.read_only
        return Dataset(
            storage=cache_chain, read_only=read_only, public=public, token=token
        )

    @staticmethod
    @hub_reporter.record_call
    def delete(path: str, force: bool = False, large_ok: bool = False) -> None:
        """Deletes a dataset"""
        raise NotImplementedError

    @staticmethod
    @hub_reporter.record_call
    def like(
        path: str,
        source: Union[str, Dataset],
        creds: dict = None,
        overwrite: bool = False,
    ) -> Dataset:
        """Copies the `source` dataset's structure to a new location. No samples are copied, only the meta/info for the dataset and it's tensors.

        Args:
            path (str): Path where the new dataset will be created.
            source (Union[str, Dataset]): Path or dataset object that will be used as the template for the new dataset.
            creds (dict): Credentials that will be used to create the new dataset.
            overwrite (bool): If True and a dataset exists at `destination`, it will be overwritten. Defaults to False.

        Returns:
            Dataset: New dataset object.
        """

        destination_ds = dataset.empty(path, creds=creds, overwrite=overwrite)
        source_ds = source
        if isinstance(source, str):
            source_ds = dataset.load(source)

        for tensor_name in source_ds.meta.tensors:  # type: ignore
            destination_ds.create_tensor_like(tensor_name, source_ds[tensor_name])

        destination_ds.info.update(source_ds.info.__getstate__())  # type: ignore

        return destination_ds

    @staticmethod
    @hub_reporter.record_call
    def ingest(
        path: str, src: str, src_creds: dict, overwrite: bool = False
    ) -> Dataset:
        """Ingests a dataset from a source"""
        raise NotImplementedError

    @staticmethod
    def list(workspace: str = "") -> None:
        """List all available hub cloud datasets.

        Args:
            workspace (str): Specify user/organization name. If not given,
                returns a list of all datasets that can be accessed, regardless of what workspace they are in.
                Otherwise, lists all datasets in the given workspace.

        Returns:
            List of dataset names.
        """
        client = HubBackendClient()
        datasets = client.get_datasets(workspace=workspace)
        return datasets
