class PocketClass:

    //** класс содержит в себе все данные и методы для обмена с одинэской

    //вероятнее всего будет синглтоном, но это в дальнейшем.. с опытом.


    /** адапторы для спиннера действий,
     * спиннера кошельков,
     * спиннера статей доходов,
     * спиннера статей расходов,
     * спиннера долгов,
     * спиннера контактов
     */

    private ArrayAdapter<String> adapterActionInOut, adapterActionImnum, adapterPurse, adapterItemsIn,
            adapterItemsOut, adapterCredits, adapterContacts;

    // соответствие остатки в кошельках (без нулевых)
    private Map<String, Double> map_pursesbalances = new Hashtable<String, Double>();

    /** соответствие последних действий. определяется для спиннеров.
     * последние действия определяются по имени или строке характеризующей элемент.
     * формат строки: Действие_Элемент/значение
     * полученное значение - значение последнего действия
     */
    private Map<String, Integer> map_lastactions = new Hashtable<String, Integer>();

    //соответствие кредита его контакту
    private Map<String, String> map_creditcontact = new Hashtable<String, String>();

    private String DIR_SD; //путь к папке с файлами на карте памяти

    private String URL; // URL по которому стучимся на веб-сервис.

    private Context MainContext; // контекст активити, которая создала объект этого класса
    private PocketInterface PocketMainContext;
    private int numth, tmpth;

    //информирует о том, что существует новый кредит - необходимо писать эту инфу в файл
    private boolean TheNewCredit;
    //////////////////////////////////////////////////////////////////


    /** необходимо инициировать для начала
     * два параметра
     * @param context контекст, чтобы потом обращаться к values
     * @param DirectoryOnSD папка на карте памяти для хранения информационных файлов.
     */
    public PocketClass(Context context, String DirectoryOnSD) {
        MainContext = context;
        DIR_SD = DirectoryOnSD;
        try {
            PocketMainContext = (PocketInterface) MainContext;
        } catch (ClassCastException e) {
            throw new ClassCastException(MainContext.toString() + " must implement PocketInterface");
        }
        initiate();
    }

    private void initiate() {
        prepareStaticSpinnerAdapters();
        prepareDynamicSpinnerAdapters();
        loadMapPurseBalaces();
        loadMapLastActions();
        loadMapCreditsContacts();
    }

    /** функция возвращает адаптер для спиннера
     */
    private ArrayAdapter<String>
    makeSpinnerAdapter(int StringResource, Boolean FromFile) {
        //прочитать файлы с исходными данными
        String[] tmp_Array;
        ArrayList<String> tmpStringList;
        if (FromFile) {
            tmpStringList = readFileToStringList(MainContext.getString(StringResource));
            //tmp_Array = tmpStringList.toArray(new String[tmpStringList.size()]);
        } else {
            tmp_Array = MainContext.getResources().getStringArray(StringResource);
            tmpStringList = new ArrayList<String>(Arrays.asList(tmp_Array));
        }

        ArrayAdapter<String> tmpAdapter = new ArrayAdapter<String>(MainContext, android.R.layout.simple_spinner_item, tmpStringList);
        tmpAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        return tmpAdapter;
    }
    private ArrayAdapter<String>
    makeSpinnerAdapter(int StringResource, Boolean FromFile,String lastItem) {
        //прочитать файлы с исходными данными
        String[] tmp_Array;
        ArrayList<String> tmpStringList;
        if (FromFile) {
            tmpStringList = readFileToStringList(MainContext.getString(StringResource));
            tmpStringList.add(lastItem);
            //tmp_Array = tmpStringList.toArray(new String[tmpStringList.size()]);
        } else {
            tmp_Array = MainContext.getResources().getStringArray(StringResource);
            tmpStringList = new ArrayList<String>(Arrays.asList(tmp_Array));
        }

        ArrayAdapter<String> tmpAdapter = new ArrayAdapter<String>(MainContext, android.R.layout.simple_spinner_item, tmpStringList);
        tmpAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        return tmpAdapter;
    }

    /** функция читает файл и возвращает массив строк
     */
    private ArrayList<String>
    readFileToStringList(String FILENAME_SD) {
        ArrayList<String> StringList = new ArrayList<String>();
        // проверяем доступность SD
        if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
            // получаем путь к SD
            File sdPath = Environment.getExternalStorageDirectory();
            // добавляем свой каталог к пути
            sdPath = new File(sdPath.getAbsolutePath() + "/" + DIR_SD);
            // формируем объект File, который содержит путь к файлу
            File sdFile = new File(sdPath, FILENAME_SD);
            try {
                // открываем поток для чтения
                BufferedReader br = new BufferedReader(new FileReader(sdFile));
                String str = "";
                // читаем содержимое
                while ((str = br.readLine()) != null) {
                    StringList.add(str);
                }
                br.close();
            } catch (FileNotFoundException e) {
                StringList.add(MainContext.getString(R.string.FileNotFound));
                //aa.add(e.getMessage());
            } catch (IOException e) {
                StringList.add(e.getMessage());
            }
        } else {
            StringList.add(MainContext.getString(R.string.BAD_SD));
        }
        return  StringList;
    }

    /** функция готовит адаптеры, которые не нужно перегружать во время работы программы
     */
    private void prepareStaticSpinnerAdapters() {
        adapterActionInOut = makeSpinnerAdapter(R.array.inout, false);
        adapterActionImnum = makeSpinnerAdapter(R.array.imnum, false);
    }
    /** функция готовит адаптеры, которые нужно перегружать после синхронизации
     */
    private void prepareDynamicSpinnerAdapters() {
        adapterPurse = makeSpinnerAdapter(R.string.FileName_purses, true);
        adapterItemsIn = makeSpinnerAdapter(R.string.FileName_initems, true);
        adapterItemsOut = makeSpinnerAdapter(R.string.FileName_outitems, true);
        adapterCredits = makeSpinnerAdapter(R.string.FileName_credits, true);
        adapterCredits.add(MainContext.getString(R.string.newCredit));
        adapterContacts = makeSpinnerAdapter(R.string.FileName_contacts, true);
        adapterContacts.add(MainContext.getString(R.string.newContact));
    }

    public ArrayAdapter<String> getAdapterActionInOut() { return adapterActionInOut; }
    public ArrayAdapter<String> getAdapterActionImnum() { return adapterActionImnum; }
    public ArrayAdapter<String> getAdapterPurse() { return adapterPurse; }
    public ArrayAdapter<String> getAdapterItemsIn() { return adapterItemsIn; }
    public ArrayAdapter<String> getAdapterItemsOut() { return adapterItemsOut; }
    public ArrayAdapter<String> getAdapterCredits() { return adapterCredits; }
    public ArrayAdapter<String> getAdapterContacts() { return adapterContacts; }

    /** процедура заполняет соответствие между кошельками и остатками
     *
     */
    private void loadMapPurseBalaces() {

        String[] tmp_pursesbalances;

        ArrayList<String> sl_pursesbalances = readFileToStringList(MainContext.getString(R.string.FileName_pursesbalances));
        tmp_pursesbalances = sl_pursesbalances.toArray(new String[sl_pursesbalances.size()]);

        map_pursesbalances.clear();
        for (String pb : tmp_pursesbalances) {
            if (pb.isEmpty()) continue;
            if (!pb.contains("/")) {
                continue;
            }
            String[] tmp_pb = pb.split("/");
            map_pursesbalances.put(tmp_pb[0], Double.parseDouble(FloatingSpace(tmp_pb[1])));
        }
    }

    /** функция исключает из строки символы, отличные от цифр, минуса и разделителя дробной части
     * числа формата ..Е+.. не рассматриваются.
     *
     */
    private String FloatingSpace(String s) {
        String dgts = MainContext.getString(R.string.dgts);
        char[] mdgts = s.replaceAll(",", ".").toCharArray();
        String fstr = new String();
        for (char n : mdgts) {
            String ts = new String() + n;
            if (dgts.contains(ts)) {
                fstr = fstr + ts;
            }
        }
        return fstr;
    }

    /** Функция
     *
     * @param purse строка имя кошелька
     * @return возвращает остаток в кошельке
     */
    public Double GetBalance(String purse) {
        if (map_pursesbalances.get(purse) == null) return 0.0;
        else return map_pursesbalances.get(purse);
    }

    ///////////////////////////////////////////////////////
    /** процедура производит изменение остатка только в мобильном приложении
     *  формирует строку для отправки в 1С
     *
     * @param purse строка имя кошелька
     * @param sum   сумма дохода
     */
    private String doIn(String purse, double sum) {
        map_pursesbalances.put(purse, GetBalance(purse) + sum);
        return "in;" + purse + ";<item>;" + String.valueOf(sum) + ";;<coment>";
    }

    /** процедура производит изменение остатка только в мобильном приложении
     *  формирует строку для отправки в 1С
     *
     * @param purse строка имя кошелька
     * @param sum   сумма расхода
     */
    private String doOut (String purse, double sum) {
        map_pursesbalances.put(purse, GetBalance(purse) - sum);
        return "out;" + purse + ";<item>;" + String.valueOf(sum) + ";;<coment>";
    }

    /** процедура производит изменение остатков только в мобильном приложении
     *  формирует строку для отправки в 1С
     *
     * @param purse1 строка имя кошелька из которого изъяли сумму
     * @param sum    сумма перемещения
     * @param purse2 строка имя кошелька в который поместили сумму
     */
    private String doBetwean (String purse1, double sum, String purse2) {
        doIn(purse2, sum);
        doOut(purse1, sum);
        return "betwean;" + purse1 + ";" + purse2 + ";" + String.valueOf(sum) + ";;<coment>";
    }

    /** процедура производит изменение остатков только в мобильном приложении
     *  формирует строку для отправки в 1С
     *
     * @param purseOut строка имя кошелька из которого изъяли сумму
     * @param sumOut    сумма расхода
     * @param purseIn строка имя кошелька в который поместили сумму (уже в другой валюте)
     * @param sumIn    сумма дохода (уже в другой валюте)
     */
    private String doExchange (String purseOut, double sumOut, String purseIn, double sumIn) {
        doIn(purseIn, sumIn);
        doOut(purseOut, sumOut);
        return "ОбменВалюты;" + purseOut + ";" + purseIn + ";" + String.valueOf(sumOut) + ";" + String.valueOf(sumIn) + ";<coment>";
    }

    // МыВернулиДолг
    private String doCreditBack(String purse, String credit, double sum , double sumPercent, double Othersum) {
        doIn(credit, sum);
        doOut(purse, sum);
        doOut(purse, sumPercent);
        doOut(purse, Othersum);
        return "МыВернулиДолг;" + purse + ";" + credit + ";" + String.valueOf(sum) + ";" +
                String.valueOf(sumPercent) + ";<coment>" + ";" + String.valueOf(Othersum) + ";" + "<contact>";
    }

    // МыВзялиВДолг
    private String doCreditTaken(String purse, String credit, double sum , double Othersum) {
        doOut(credit, sum);
        doIn(purse, sum);
        doOut(purse, Othersum);
        return "МыВзялиВДолг;" + purse + ";" + credit + ";" + String.valueOf(sum) + ";" +
                String.valueOf(Othersum) + ";<coment>" + ";;" + "<contact>";
    }

    // МыДалиВДолг
    private String doCreditGiven(String purse, String credit, double sum , double Othersum) {
        doIn(credit, sum);
        doOut(purse, sum);
        doOut(purse, Othersum);
        return "МыДалиВДолг;" + purse + ";" + credit + ";" + String.valueOf(sum) + ";" +
                String.valueOf(Othersum) + ";<coment>" + ";;" + "<contact>";
    }

    // НамВернулиДолг
    private String doReturnCredit(String purse, String credit, double sum , double sumPercent) {
        doOut(credit, sum);
        doIn(purse, sum);
        doIn(purse, sumPercent);
        return "НамВернулиДолг;" + purse + ";" + credit + ";" + String.valueOf(sum) + ";" +
                String.valueOf(sumPercent) + ";<coment>" + ";;" + "<contact>";
    }

    /** процедура выполняет необходимое движение денег
     *
     * @param index 1-доход, 2-расход, 3-перемещение, 4-обмен валюты
     * @param purse1 кошелек
     * @param sum1   сумма
     * @param item   статья движения
     * @param purse2 кошелек
     * @param sum2   сумма
     * @param coment комментарий
     */
    public void DoAction(int index, String purse1, double sum1, String item, String purse2, double sum2, String coment, double sum3, String contact) {
        String dataFor1c = new String();
        switch (index) {
            case 0: //доход
                dataFor1c = doIn(purse1, sum1);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"ItemIn",item);
                break;
            case 1: //расход
                dataFor1c = doOut(purse1, sum1);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"ItemOut",item);
                break;
            case 2: //перемещение
                dataFor1c = doBetwean(purse1, sum1, purse2);
                setLastAction(index,"PurseOut",purse1);
                setLastAction(index,"PurseIn",purse2);
                break;
            case 3: //обмен валюты
                dataFor1c = doExchange(purse1, sum1, purse2, sum2);
                setLastAction(index,"PurseOut",purse1);
                setLastAction(index,"PurseIn",purse2);
                break;
            case 4: // МыВернулиДолг
                dataFor1c = doCreditBack(purse1, item, sum1, sum2, sum3);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"Credit",item);
                break;
            case 5: // МыВзялиВДолг
                dataFor1c = doCreditTaken(purse1, item, sum1, sum3);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"Credit",item);
                break;
            case 6: // МыДалиВДолг
                dataFor1c = doCreditGiven(purse1, item, sum1, sum3);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"Credit",item);
                break;
            case 7: // НамВернулиДолг
                dataFor1c = doReturnCredit(purse1, item, sum1, sum2);
                setLastAction(index,"Purse",purse1);
                setLastAction(index,"Credit",item);
                break;
            default:
                break;
        }
        dataFor1c = dataFor1c.replace("<item>",item);
        dataFor1c = dataFor1c.replace("<coment>", coment);
        dataFor1c = dataFor1c.replace("<contact>", contact);
        if (index > 3) ChekNewCredit(item, contact);
        writeFileFor1C(dataFor1c);
        setLastAction("Action", index);
        (new BackGroundDumping()).execute();
    }

    /** процедура выполняет необходимое движение денег
     *
     * @param lAction действие
     * @param purse1 кошелек
     * @param sum1   сумма
     * @param item   статья движения
     * @param purse2 кошелек
     * @param sum2   сумма
     * @param coment комментарий
     */
    public void DoAction(String lAction, String purse1, double sum1, String item, String purse2, double sum2, String coment, double sum3, String contact) {

        int index = adapterActionInOut.getPosition(lAction);

        if (index < 0) {
            index = adapterActionInOut.getCount() + adapterActionImnum.getPosition(lAction);
        }
        if (index != adapterActionInOut.getCount() + adapterActionImnum.getCount()) {
            DoAction(index, purse1, sum1, item, purse2, sum2, coment, sum3, contact);
        }
    }

    /** процедура выполняет синхронизацию файлов с 1С
     *
     */
    public void DoSynchronisation() {
        String[] tmp_actions;

        //if (!CheckAuth()) return;

        ArrayList<String> sl_actions = readFileToStringList(MainContext.getString(R.string.FileName_actions));
        tmp_actions = sl_actions.toArray(new String[sl_actions.size()]);

        tmpth = 0;
        numth = tmp_actions.length;
        if (tmp_actions[0].equals(MainContext.getString(R.string.FileNotFound))) numth--;
        //PocketMainContext.ItIsProgressTotal(numth + 4);
        PocketMainContext.ItIsProgressTotal(numth + 1);
        if (!tmp_actions[0].equals(MainContext.getString(R.string.FileNotFound))) {
            for (String st : tmp_actions) {
                (new Class_Soap_Data_1C()).execute("0", st);
            }
        }
        (new Class_Soap_Data_1C()).execute("2", "");
    }

    ///////////////////////////////////////////////////////

    /** процедура записи файла, который потом будет отослан в веб-сервис 1С
     *
     * @param aa строка для записи, разделенная точками с запятой.
     *           содержание строчки в общем виде:
     *                  - кошелек
     *                  - статья
     *                  - сумма
     *                  - количество
     *                  - комментарий
     *                  потом будет еще
     */
    private void writeFileFor1C(String aa) {
        // проверяем доступность SD
        if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
            // получаем путь к SD
            File sdPath = Environment.getExternalStorageDirectory();
            // добавляем свой каталог к пути
            sdPath = new File(sdPath.getAbsolutePath() + "/" + MainContext.getString(R.string.DIR_SD));
            if (!sdPath.exists()) { //Если папка не существует
                sdPath.mkdirs();  //создаем её
            }
            // формируем объект File, который содержит путь к файлу
            File sdFile = new File(sdPath, MainContext.getString(R.string.FileName_actions));
            try {
                // открываем поток для записи в конец файла
                BufferedWriter bw = new BufferedWriter(new FileWriter(sdFile, true));
                // дописываем содержимое
                try {
                    bw.write(aa);
                    bw.write(MainContext.getString(R.string.tudasuda));
                } catch (IOException e) {
                    //пока такого не возникало.. позырим со временем.
                    bw.newLine();
                    bw.write(aa);
                    bw.write(MainContext.getString(R.string.tudasuda));
                }
                bw.close();
            } catch (Exception e) {
                //хз чо тут делать... делать нечего. да, исключение.
                PocketMainContext.ItIsErrorDuringSync(true);
            }
        }
    }

    /** функция определяет наличие файла для отправки в 1С
     *
     * @return -1, если не доступна SD карта
     *         0, если файла нет, или нет директории на карте памяти, в которой должен быть файл
     *         1, если файл существует.
     */
    public Integer GetExchangeNeed() {
        int rslt = -1;
        // проверяем доступность SD
        if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
            // получаем путь к SD
            File sdPath = Environment.getExternalStorageDirectory();
            // добавляем свой каталог к пути
            sdPath = new File(sdPath.getAbsolutePath() + "/" + MainContext.getString(R.string.DIR_SD));
            if (!sdPath.exists()) { //Если папка не существует
                rslt = 0;
            }
            // формируем объект File, который содержит путь к файлу
            File sdFile = new File(sdPath, MainContext.getString(R.string.FileName_actions));
            if (!sdFile.exists()) { //Если файл не существует
                rslt = 0;
            } else rslt = 1;
        }
        return rslt;
    }

    /** процедура загружает из файла информацию о последних действиях для каждого действия
     *
     */
    private void loadMapLastActions() {
        String[] tmp_LastActions;

        ArrayList<String> sl_LastActions = readFileToStringList(MainContext.getString(R.string.FileName_LastActions));
        tmp_LastActions = sl_LastActions.toArray(new String[sl_LastActions.size()]);

        map_lastactions.clear();
        for (String pb : tmp_LastActions) {
            if (pb.isEmpty()) continue;
            if (!pb.contains("/")) continue;
            String[] tmp_pb = pb.split("/");
            map_lastactions.put(tmp_pb[0], Integer.parseInt(FloatingSpace(tmp_pb[1])));
        }
    }

    /** процедура устанавливает значения в соответствие последних действий
     *
     * @param lAction   индекс последнего действия
     * @param ValueName имя по которому при получении данных будет определяться значение
     * @param ValueData выбранное значение переменной ValueName
     */
    private void setLastAction(int lAction, String ValueName, String ValueData) {
        int intValueData = 0;
        if (ValueName.equals("Purse") || ValueName.equals("PurseOut") || ValueName.equals("PurseIn")) {
            intValueData = adapterPurse.getPosition(ValueData);
        }
        if (ValueName.equals("ItemIn")) {
            intValueData = adapterItemsIn.getPosition(ValueData);
        }
        if (ValueName.equals("ItemOut")) {
            intValueData = adapterItemsOut.getPosition(ValueData);
        }
        if (ValueName.equals("Credit")) {
            intValueData = adapterCredits.getPosition(ValueData);
        }
        map_lastactions.put(String.valueOf(lAction) + "_" + ValueName, intValueData);
    }

    /** процедура устанавливает значения в соответствие последних действий
     *
     * @param ValueName скорее всего "Action"
     * @param ValueData выбранное значение переменной ValueName
     */
    private void setLastAction(String ValueName, int ValueData) { map_lastactions.put(ValueName, ValueData); }

    /** функция возвращает индекс значения требуемого списка значений для конкретного действия
     *
     * @param lAction   индекс действия
     * @param ValueName имя по которому определяется значение
     * @return
     */
    public int getLastAction(String lAction, String ValueName) {
        if (map_lastactions.get(lAction+"_"+ValueName) == null) return 0;
        else return map_lastactions.get(lAction+"_"+ValueName);
    }

    /** функция возвращает индекс действия списка значений действий
     *
     * @param lAction скорее всего "Action"
     * @return
     */
    public int getLastAction(String lAction) {
        if (map_lastactions.get(lAction) == null) return 0;
        else return map_lastactions.get(lAction);
    }

    /** процедура загружает из файла соответствия кредитов их контактам
     */
    private void loadMapCreditsContacts() {
        String[] tmp_сс;

        ArrayList<String> sl_cc = readFileToStringList(MainContext.getString(R.string.FileName_creditscontacts));
        tmp_сс = sl_cc.toArray(new String[sl_cc.size()]);

        map_creditcontact.clear();
        for (String pb : tmp_сс) {
            if (pb.isEmpty()) continue;
            if (!pb.contains("/")) continue;
            String[] tmp_pb = pb.split("/");
            map_creditcontact.put(tmp_pb[0], tmp_pb[1]);
        }
    }

    /** функция ищет контакт, которому принадлежит данный кредит
     *
     * @param credit наименование кредита
     * @return имя контакта
     */
    public String GetCreditContact(String credit) {
        if (map_creditcontact.get(credit) == null) return "";
        return map_creditcontact.get(credit);
    }

    /** процедура проверяет наличие контакта в списке контактов и кредита в списке кредитов.
     * если не обнаружено совпадений, то добавляет в конец новое значение.
     *
     * @param credit
     * @param contact
     */
    private void ChekNewCredit(String credit, String contact) {
        TheNewCredit = false;
        if (adapterContacts.getPosition(contact) == -1) {
            TheNewCredit = true;
            adapterContacts.add(contact);
        }
        if (adapterCredits.getPosition(credit) == -1) {
            TheNewCredit = true;
            adapterCredits.add(credit);
            map_creditcontact.put(credit, contact);
        }
    }
    ///////////////////////////////////////////////////////

    /** класс для выполнения запросов к сервису 1С в отдельном потоке.
     * Параметры запуска execute(..) - строковые.
     *      "0" - запуск отправки действий в 1С
     *              вторым параметром идет строчка с действиями
     *      "1" - запуск получения данных о кошельках, статьях, остатках.
     *              вторым параметром идет номер запроса в 1Ске. от "0" до "4".. пока. доделать.
     */
    private class Class_Soap_Data_1C extends AsyncTask<String, Void, Integer> {

        @Override
        protected Integer doInBackground(String... params) {
            int rslt = -1;
            int param0 = Integer.parseInt(params[0]);
            switch (param0) {
                case 0:
                    rslt = Send_Soap_Service_Data(params[1]);
                    break;
                case 1:
                    while (numth != tmpth) {
                        try {
                            Thread.sleep(250);
                        } catch (InterruptedException e) {
                            // this is executed when an exception (in this example InterruptedException) occurs
                            PocketMainContext.ItIsErrorDuringSync(true);
                        }
                    }
                    rslt = Get_Soap_Service_Data(params[1]);
                    break;
                case 2:
                    rslt = Get_Soap_Service_Data();
                    break;
            }
            return rslt;
        }

        @Override
        protected void onPostExecute(Integer result) {
            tmpth++;
            PocketMainContext.ItIsProgressNow(tmpth);
            if (result == 0) // 0 - то, что возвращает функция посыла в 1С в случае успеха.
            {
                removefile(MainContext.getString(R.string.FileName_actions));
            }
            if (result == -1) {
                // что-то пошло не так.
                PocketMainContext.ItIsErrorDuringSync(false);
            }
            //if (numth + 4 == tmpth) {
            if (numth + 1 == tmpth) {
                prepareDynamicSpinnerAdapters();
                loadMapPurseBalaces();
                PocketMainContext.ItIsNewData();
            }
        }
    }

    /** класс для выполнения запросов к сервису 1С в отдельном потоке.
     * Параметры запуска execute(..) - строковые.
     *      "2" - запуск отправки действий в 1С
     *              вторым параметром идет строчка с действиями
     */
    private class Class_Soap_Data_1C_report extends AsyncTask<Integer, Void, String> {

        @Override
        protected String doInBackground(Integer... params) {
            return Get_Soap_Service_TextHTML(params[0]);
        }

        @Override
        protected void onPostExecute(String result) {
            PocketMainContext.ItIsReport(result);
        }
    }

    /** процедура удаляет файл с карты памяти из нашего каталога.
     *
     * @param FILENAME_SD имя файла на карте памяти
     */
    private void removefile(String FILENAME_SD) {
        if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
            File sdPath = Environment.getExternalStorageDirectory();
            sdPath = new File(sdPath.getAbsolutePath() + "/" + MainContext.getString(R.string.DIR_SD));
            File sdFile = new File(sdPath, FILENAME_SD);
            sdFile.delete();
        } else {
            //Log.i("Removing_File_actions", getString(R.string.BAD_SD));
        }
    }

    /** функция возвращает закодированную строку логина и пароля для авторизации в веб-сервисе 1С
     */
    public String Form_Header() {
        String res_str = new String();
        try {
            // открываем поток для чтения
            BufferedReader br = new BufferedReader(new InputStreamReader(
                    MainContext.openFileInput(MainContext.getString(R.string.auth_file))));
            // читаем содержимое
            res_str = br.readLine();
            URL = br.readLine();
        } catch (Exception e) {
            PocketMainContext.ItIsErrorDuringSync(true);
        }
        return res_str;
    }

    /** функция отправляет строку данных по учету (из файла actions.txt)
     *
     * @param Param_For_Remote_Function строка с данными
     * @return -1 в случае неудачного обращения к сервису 1С, иначе 0.
     */
    private Integer Send_Soap_Service_Data(String Param_For_Remote_Function) {

        int Otkaz = 0;

        String SOAP_ACTION = MainContext.getString(R.string.SOAP_ACTION);
        String SOAP_METHOD_NAME = MainContext.getString(R.string.SOAP_METHOD_NAME);
        //String URL = MainContext.getString(R.string.URL);
        String NAMESPACE = MainContext.getString(R.string.NAMESPACE);

        SoapObject Request = new SoapObject(NAMESPACE, SOAP_METHOD_NAME);

        // here you form body of your SOAP-request
        Request.addProperty(MainContext.getString(R.string.SOAP_property_actions), Param_For_Remote_Function);

        SoapSerializationEnvelope soapEnvelope = new SoapSerializationEnvelope(SoapEnvelope.VER11);
        //soapEnvelope.dotNet = true;

        soapEnvelope.setAddAdornments(false);
        soapEnvelope.encodingStyle = SoapSerializationEnvelope.ENC;
        soapEnvelope.env = SoapSerializationEnvelope.ENV;
        soapEnvelope.implicitTypes = true;

        List<HeaderProperty> headerPropertyList = new ArrayList<HeaderProperty>();
        headerPropertyList.add(new HeaderProperty(MainContext.getString(R.string.SOAP_Auth), Form_Header()));

        soapEnvelope.setOutputSoapObject(Request);

        HttpTransportSE aht = new HttpTransportSE(URL); // перед вызовом URL обязательно он должен быть задан. а задается он функцией Form_Header()
        //aht.debug = true;

        try {
            aht.call(SOAP_ACTION, soapEnvelope, headerPropertyList);
            SoapPrimitive resultString = (SoapPrimitive) soapEnvelope.getResponse();
        } catch (Exception e) {
            Otkaz = -1;
        }
        return Otkaz;
    }

    /** функция получает от сервиса 1С данные для записи в файл.
     *
     * @param Param_For_Remote_Function строка с числовым значением
     *                                  1: кошельки
     *                                  2: статьи дохода
     *                                  3: статьи расхода
     *                                  4: остатки
     *                                  пусто, если данные для нового функционала
     * @return -1 в случае неудачного запроса к сервису, иначе 1.
     */
    private Integer Get_Soap_Service_Data(String Param_For_Remote_Function) {

        int rslt = 1;

        int parameter = Integer.parseInt(Param_For_Remote_Function);

        //String URL = MainContext.getString(R.string.URL);
        String NAMESPACE = MainContext.getString(R.string.NAMESPACE);
        String SOAP_ACTION2 = MainContext.getString(R.string.SOAP_ACTION2);
        String SOAP_METHOD_NAME2 = MainContext.getString(R.string.SOAP_METHOD_NAME2);

        SoapObject Request = new SoapObject(NAMESPACE, SOAP_METHOD_NAME2);

        // here you form body of your SOAP-request
        Request.addProperty(MainContext.getString(R.string.SOAP_property_what), parameter);

        SoapSerializationEnvelope soapEnvelope = new SoapSerializationEnvelope(SoapEnvelope.VER11);
        //soapEnvelope.dotNet = true;

        soapEnvelope.setAddAdornments(false);
        soapEnvelope.encodingStyle = SoapSerializationEnvelope.ENC;
        soapEnvelope.env = SoapSerializationEnvelope.ENV;
        soapEnvelope.implicitTypes = true;


        List<HeaderProperty> headerPropertyList = new ArrayList<HeaderProperty>();
        headerPropertyList.add(new HeaderProperty(MainContext.getString(R.string.SOAP_Auth), Form_Header()));

        soapEnvelope.setOutputSoapObject(Request);

        HttpTransportSE aht = new HttpTransportSE(URL); // перед вызовом URL обязательно он должен быть задан. а задается он функцией Form_Header()
//        aht.debug = true;

        try {
            aht.call(SOAP_ACTION2, soapEnvelope, headerPropertyList);
            SoapPrimitive resultString = (SoapPrimitive) soapEnvelope.getResponse();

            switch (parameter) {
                case 1:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_purses));
                    break;
                case 2:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_initems));
                    break;
                case 3:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_outitems));
                    break;
                case 4:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_pursesbalances));
                    break;
            }

        } catch (Exception e) {
            rslt = -1;
        }
        return rslt;
    }
    private Integer Get_Soap_Service_Data() {

        int rslt = 1;

        //String URL = MainContext.getString(R.string.URL);
        String NAMESPACE = MainContext.getString(R.string.NAMESPACE);
        String SOAP_ACTION2 = MainContext.getString(R.string.SOAP_ACTION3);
        String SOAP_METHOD_NAME2 = MainContext.getString(R.string.SOAP_METHOD_NAME3);

        SoapObject Request = new SoapObject(NAMESPACE, SOAP_METHOD_NAME2);

        SoapSerializationEnvelope soapEnvelope = new SoapSerializationEnvelope(SoapEnvelope.VER11);
        //soapEnvelope.dotNet = true;

        soapEnvelope.setAddAdornments(false);
        soapEnvelope.encodingStyle = SoapSerializationEnvelope.ENC;
        soapEnvelope.env = SoapSerializationEnvelope.ENV;
        soapEnvelope.implicitTypes = true;


        List<HeaderProperty> headerPropertyList = new ArrayList<HeaderProperty>();
        headerPropertyList.add(new HeaderProperty(MainContext.getString(R.string.SOAP_Auth), Form_Header()));

        soapEnvelope.setOutputSoapObject(Request);

        HttpTransportSE aht = new HttpTransportSE(URL); // перед вызовом URL обязательно он должен быть задан. а задается он функцией Form_Header()
//        aht.debug = true;

        try {
            aht.call(SOAP_ACTION2, soapEnvelope, headerPropertyList);
            SoapObject resultObj = (SoapObject) soapEnvelope.getResponse();

            int totalCount = resultObj.getPropertyCount();
            if (totalCount > 0 ) {
                for (int parameter = 0; parameter < totalCount; parameter ++) {
                    SoapObject strObj = (SoapObject) resultObj.getProperty(parameter);
                    switch (parameter) {
                        case 0:
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_purses));
                            break;
                        case 1:
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_initems));
                            break;
                        case 2:
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_outitems));
                            break;
                        case 3:
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_pursesbalances));
                            break;
                        case 4: //кредиты
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_credits));
                            break;
                        case 5: //контакты
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_contacts));
                            break;
                        case 6: //кредиты/контакты
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_creditscontacts));
                            break;
                        case 7: //кошельки/валюты
                            writeDataFile(strObj.getProperty(0).toString(), MainContext.getString(R.string.FileName_pursescurrencies));
                            break;
                    }
                }
            }

//            for (String ap : resultString.getValue()) {
//                parameter++;
//
//            }



        } catch (Exception e) {
            rslt = -1;
        }
        return rslt;
    }

    /** функция получает от сервиса 1С текст отчета.
     *
     * @param Param_For_Remote_Function строка с числовым значением
     *                                  1: за день
     *                                  2: за неделю
     *                                  3: за месяц
     *                                  4: за год
     * @return "-1" в случае неудачного запроса к сервису, иначе 1.
     */
    private String Get_Soap_Service_TextHTML(int Param_For_Remote_Function) {

        String rslt = "";

        int parameter = Param_For_Remote_Function;

        //String URL = MainContext.getString(R.string.URL);
        String NAMESPACE = MainContext.getString(R.string.NAMESPACE);
        String SOAP_ACTION2 = MainContext.getString(R.string.SOAP_ACTION4);
        String SOAP_METHOD_NAME2 = MainContext.getString(R.string.SOAP_METHOD_NAME4);

        SoapObject Request = new SoapObject(NAMESPACE, SOAP_METHOD_NAME2);

        // here you form body of your SOAP-request
        Request.addProperty(MainContext.getString(R.string.SOAP_property_param), parameter);

        SoapSerializationEnvelope soapEnvelope = new SoapSerializationEnvelope(SoapEnvelope.VER11);
        //soapEnvelope.dotNet = true;

        soapEnvelope.setAddAdornments(false);
        soapEnvelope.encodingStyle = SoapSerializationEnvelope.ENC;
        soapEnvelope.env = SoapSerializationEnvelope.ENV;
        soapEnvelope.implicitTypes = true;


        List<HeaderProperty> headerPropertyList = new ArrayList<HeaderProperty>();
        headerPropertyList.add(new HeaderProperty(MainContext.getString(R.string.SOAP_Auth), Form_Header()));

        soapEnvelope.setOutputSoapObject(Request);

        HttpTransportSE aht = new HttpTransportSE(URL); // перед вызовом URL обязательно он должен быть задан. а задается он функцией Form_Header()
//        aht.debug = true;

        try {
            aht.call(SOAP_ACTION2, soapEnvelope, headerPropertyList);
            SoapPrimitive resultString = (SoapPrimitive) soapEnvelope.getResponse();

            rslt = resultString.getValue().toString();
        } catch (Exception e) {
            rslt = e.getMessage();
        }
        return rslt;
    }

    /** процедура записывает на карту памяти данные, полученные от веб-сервиса 1С в файлы
     *
     * @param aa              строка с данными, разделенными точкой с запятой
     * @param FILENAME_SD     имя файла в который нужно записать эти данные
     */
    private void writeDataFile(String aa, String FILENAME_SD) {
        if (Environment.getExternalStorageState().equals(Environment.MEDIA_MOUNTED)) {
            File sdPath = Environment.getExternalStorageDirectory();
            sdPath = new File(sdPath.getAbsolutePath() + "/" + MainContext.getString(R.string.DIR_SD));
            if (!sdPath.exists()) { //Если папка не существует
                sdPath.mkdirs();  //создаем её
            }
            File sdFile = new File(sdPath, FILENAME_SD);
            try {
                BufferedWriter bw = new BufferedWriter(new FileWriter(sdFile, false));
                String[] newaa = aa.split(";");
                for (String tmpaa : newaa) {
                    bw.write(tmpaa);
                    bw.newLine();
                }
                bw.close();
            } catch (Exception e) {
                PocketMainContext.ItIsErrorDuringSync(true);
            }
        }
    }


    ////////////////////////////////////////////////////////////

    /** интерфейс для оповещения UI класса информацией по обмену
     * UI класс должен имплементить этот интерфейс
     */
    public interface PocketInterface {
        public void ItIsProgressTotal(int AsyncTotal);
        public void ItIsProgressNow(int AsyncProgress);
        public void ItIsNewData();
        public void ItIsErrorDuringSync(boolean byExeption);
        public void ItIsReport(String data);
    }

    ////////////////////////////////////////////////////////////

    private class BackGroundDumping extends AsyncTask<Void,Void,Void> {

        @Override
        protected Void doInBackground(Void... params) {
            String fstr = new String();
            for (Map.Entry<String, Double> entry : map_pursesbalances.entrySet()) {
                fstr = fstr + ";" + entry.getKey() + "/" + entry.getValue().toString();
            }
            writeDataFile(fstr, MainContext.getString(R.string.FileName_pursesbalances));

            fstr = new String();
            for (Map.Entry<String, Integer> entry : map_lastactions.entrySet()) {
                fstr = fstr + ";" + entry.getKey() + "/" + entry.getValue().toString();
            }
            writeDataFile(fstr, MainContext.getString(R.string.FileName_LastActions));

            if (TheNewCredit) {
                fstr = new String();
                for (Map.Entry<String, String> entry : map_creditcontact.entrySet()) {
                    fstr = fstr + ";" + entry.getKey() + "/" + entry.getValue();
                }
                writeDataFile(fstr, MainContext.getString(R.string.FileName_creditscontacts));

                fstr = new String();
                int countC = adapterCredits.getCount();
                for (int i = 0; i<countC; i++ ) {
                    String entry = adapterCredits.getItem(i);
                    fstr = fstr + ";" + entry;
                }
                writeDataFile(fstr, MainContext.getString(R.string.FileName_credits));

                fstr = new String();
                countC = adapterContacts.getCount();
                for (int i = 0; i<countC; i++ ) {
                    String entry = adapterContacts.getItem(i);
                    fstr = fstr + ";" + entry;
                }
                writeDataFile(fstr, MainContext.getString(R.string.FileName_contacts));
            }
            return null;
        }
    }

    /** процедура инициализирует запрос для отчета
     *
     * @param param 1 - за день
     *              2 - за неделю
     *              3 - за месяц
     *              4 - за год
     */
    public void doReport(int param) {
        (new Class_Soap_Data_1C_report()).execute(param);
        (new Class_Soap_Data_1C()).execute("2", "");
    }

    /** функция возвращает в формате HTML таблички с остатками
     *
     * @return
     */
    public String HTMLBalances() {
        Map<String, String> map_pursesCurrencys = new Hashtable<String, String>();
        Map<String, Double> map_Currencystotal = new Hashtable<String, Double>();
        String[] tmp_pс;
        ArrayList<String> sl_pc = readFileToStringList(MainContext.getString(R.string.FileName_pursescurrencies));
        tmp_pс = sl_pc.toArray(new String[sl_pc.size()]);
        map_pursesCurrencys.clear();
        map_Currencystotal.clear();
        for (String pb : tmp_pс) {
            if (pb.isEmpty()) continue;
            if (!pb.contains("/")) continue;
            String[] tmp_pb = pb.split("/");
            map_pursesCurrencys.put(tmp_pb[0], tmp_pb[1]);
            // map_Currencystotal.put(tmp_pb[1], 0.0);
        }

        String rslt = "<html><body><table width=100% border=0 cellspacing=0>" +
                "<tr><td align=center>Объект</td><td align=center>Баланс</td></tr></table>" +
                "<table width=100% border=1 cellspacing=0>";
        double local;
        double total;
        //String prs;
        String[] entrst = map_pursesbalances.keySet().toArray(new String[map_pursesbalances.keySet().size()]);
        Arrays.sort(entrst);
        for (String prs : entrst) {
            //prs = entry.getKey();
            local =  map_pursesbalances.get(prs);
            String crnc = new String();
            try {
                crnc = map_pursesCurrencys.get(prs);
            } catch (Exception e) {}
            rslt = rslt + "<tr><td>" + prs + ", " + crnc + "</td><td align=right><nobr>" +String.valueOf(local) + "</nobr></td></tr>";
            total = 0;
            try {
                total = map_Currencystotal.get(crnc);
            } catch (Exception e) {}
            map_Currencystotal.put(crnc,total + local);
        }
        rslt = rslt + "</table><br>Финансовый результат<br><table width=100% border=1 cellspacing=0>";
        for (Map.Entry<String, Double> entry : map_Currencystotal.entrySet()) {
            rslt = rslt + "<tr><td>" + entry.getKey() + "</td><td align=right><nobr>" + String.valueOf(entry.getValue()) + "</nobr></td></tr>";
        }
        rslt = rslt + "</table>";
        rslt = rslt.concat("</body></html>");
        return rslt;
    }

}
